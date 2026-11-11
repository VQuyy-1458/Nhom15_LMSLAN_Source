"""System taxonomy, teacher administration and owned content classification."""
import json
import copy
import secrets

from . import permissions
from .storage import read_json, write_json, utc_now, audit, atomic_transaction

DIFFICULTIES = {"easy":"Dễ", "medium":"Trung bình", "hard":"Khó"}
LANGUAGES = {"c":"C", "cpp":"C++", "java":"Java", "python":"Python"}
TARGETS = {"assignment":"programming_assignments.json", "exam":"exam_catalog.json", "question":"questions.json"}


def values(form, key, default):
    from .learning import LearningError
    raw = form.get(key, default)
    try:
        result = json.loads(raw) if isinstance(raw,str) else raw
        if not isinstance(result,list) or len(result)>100 or any(not isinstance(v,str) for v in result):
            raise ValueError()
        return list(dict.fromkeys(result))
    except (ValueError,TypeError):
        raise LearningError(400, "Danh sách danh mục không hợp lệ.")


def metadata(form, old=None):
    from .learning import LearningError
    old = old or {}
    topics = values(form,"topic_ids",old.get("topic_ids",[]))
    difficulty = form.get("difficulty",old.get("difficulty","medium"))
    languages = values(form,"classification_languages",old.get("classification_languages",[]))
    if difficulty not in DIFFICULTIES or any(v not in LANGUAGES for v in languages):
        raise LearningError(400,"Độ khó hoặc ngôn ngữ phân loại không hợp lệ.")
    catalog = {r["id"]:r for r in read_json("topics.json",[])}
    if any(t not in catalog or (not catalog[t].get("active",True) and t not in old.get("topic_ids",[])) for t in topics):
        raise LearningError(400,"Chủ đề không tồn tại hoặc đã ngừng sử dụng.")
    return {"topic_ids":topics,"difficulty":difficulty,"classification_languages":languages}


def target(kind,item_id,session):
    from .learning import LearningError
    if kind not in TARGETS:
        raise LearningError(400,"Loại nội dung không hợp lệ.")
    rows = read_json(TARGETS[kind],[])
    row = next((r for r in rows if r["id"] == item_id),None)
    if row is None:
        raise LearningError(404,"Không tìm thấy nội dung.")
    permissions.require_content(session,row)
    return rows,row


def validate_languages(row):
    from .learning import LearningError
    if row.get("programming") and not set(row.get("classification_languages",[])).issubset(row["programming"]["languages"]):
        raise LearningError(400,"Ngôn ngữ phân loại phải nằm trong các ngôn ngữ được phép chạy của nội dung.")


def snapshot(session):
    from .learning import load
    from . import question_library
    if not permissions.staff(session):
        permissions.deny()
    courses = [c for c in load()["courses"] if permissions.course_allowed(session,c["id"])]
    result = {"topics":read_json("topics.json",[]),"difficulties":DIFFICULTIES,"languages":LANGUAGES,
              "courses":[{"id":c["id"],"name":c["name"],"teacher_ids":c.get("teacher_ids",[])} for c in courses],
              "content":[], "purposes":question_library.PURPOSES, "response_types":question_library.FORMATS,
              "papers":question_library.papers(session)}
    for kind,store in TARGETS.items():
        for row in read_json(store,[]):
            if not row.get("archived") and permissions.manages(session,row):
                result["content"].append({**row,"content_type":kind})
    if session["role"] == "admin":
        result["teachers"] = [{"id":name,"full_name":r.get("full_name",name),"active":r.get("active",True)} for name,r in read_json("teachers.json",{}).items()]
    return result


def manage(session, action, form, ip):
    from . import learning, exam_catalog, question_library
    from .security import hash_password
    if not permissions.staff(session):
        permissions.deny()
    with learning.LOCK,atomic_transaction():
        if action in {"topic-save","topic-archive","teacher-save","course-teachers"} and session["role"] != "admin":
            permissions.deny("Chỉ Admin được quản lý danh mục, giáo viên và phân công khóa học.")
        if action.startswith("topic-"):
            rows = read_json("topics.json",[])
            row = next((r for r in rows if r["id"]==form.get("id")),None)
            if form.get("id") and not row:
                raise learning.LearningError(404,"Không tìm thấy chủ đề.")
            if action=="topic-archive":
                if not row: raise learning.LearningError(404,"Không tìm thấy chủ đề.")
                row["active"]=False
            else:
                name=learning.text(form,"name",120)
                if any(r["name"].casefold()==name.casefold() and r is not row for r in rows):
                    raise learning.LearningError(409,"Chủ đề đã tồn tại.")
                if row is None:
                    row={"id":secrets.token_hex(10),"active":True,"created_at":utc_now()};rows.append(row)
                row["name"]=name
            write_json("topics.json",rows)
        elif action=="teacher-save":
            name=learning.text(form,"id",80)
            if not all(c.isalnum() or c in "._-@" for c in name):
                raise learning.LearningError(400,"Tên tài khoản không hợp lệ.")
            if name in read_json("admins.json") or name in read_json("students.json"):
                raise learning.LearningError(409,"Tên tài khoản đã được sử dụng.")
            teachers=read_json("teachers.json",{})
            old=teachers.get(name,{})
            password=form.get("password","")
            if (not old or password) and not 8<=len(password)<=200:
                raise learning.LearningError(400,"Mật khẩu giáo viên cần từ 8 đến 200 ký tự.")
            active=form.get("active","true")
            if active not in {"true","false"}:raise learning.LearningError(400,"Trạng thái không hợp lệ.")
            teachers[name]={**old,"full_name":learning.text(form,"full_name"),"active":active=="true","created_at":old.get("created_at",utc_now())}
            if password:teachers[name]["password_hash"]=hash_password(password)
            write_json("teachers.json",teachers)
            if password or active=="false":
                sessions=read_json("sessions.json")
                write_json("sessions.json",{k:v for k,v in sessions.items() if not(v["role"]=="teacher" and v["user_id"]==name)})
        elif action=="course-teachers":
            data=learning.load();course=learning.find(data,"courses",learning.text(form,"course_id",80))
            if "teacher_ids" not in form:
                raise learning.LearningError(400,"Thiếu danh sách giáo viên được phân công. Hãy chọn giáo viên rồi lưu.")
            ids=values(form,"teacher_ids",[]);teachers=read_json("teachers.json",{})
            if any(i not in teachers or not teachers[i].get("active",True) for i in ids):
                raise learning.LearningError(400,"Danh sách có giáo viên không tồn tại hoặc đã bị khóa.")
            course["teacher_ids"]=ids;write_json("learning.json",data)
        elif action=="assign":
            kind=form.get("content_type");rows,row=target(kind,form.get("id"),session)
            learning.course_access(learning.load(),row["course_id"],session,write=True) if row.get("course_id") else None
            row.update(metadata(form,row));row["content_type"]=kind;row["updated_at"]=utc_now()
            if kind == "question":
                if form.get("response_type",row.get("response_type","code"))!=row.get("response_type","code"):
                    raise learning.LearningError(400,"Hãy tạo phiên bản câu hỏi mới để đổi hình thức.")
                row.update(question_library.question_metadata(form, row))
                question_library.sync_file_practice(row)
            validate_languages(row)
            write_json(TARGETS[kind],rows)
        elif action.startswith("question-"):
            rows=read_json("questions.json",[])
            row=next((r for r in rows if r["id"]==form.get("id")),None)
            if form.get("id") and row is None:raise learning.LearningError(404,"Không tìm thấy câu hỏi.")
            if row is not None:permissions.require_content(session,row)
            course_id=row["course_id"] if row else learning.text(form,"course_id",80)
            permissions.require_course(session,course_id)
            learning.course_access(learning.load(),course_id,session,write=True)
            if row and row.get("archived"):
                raise learning.LearningError(409,"Câu hỏi đã lưu trữ, không thể tiếp tục sử dụng.")
            if action=="question-clone":
                if not row:raise learning.LearningError(404,"Không tìm thấy câu hỏi.")
                clone={**copy.deepcopy(row),"id":"q_"+secrets.token_hex(12),"published":False,
                       "created_by":session["user_id"],"created_at":utc_now(),"source_question_id":row["id"]}
                rows.append(clone);write_json("questions.json",rows)
                audit("classification.question-clone",session["user_id"],ip,{"source_id":row["id"],"id":clone["id"]})
                return {"ok":True,"id":clone["id"]}
            if action=="question-reuse":
                if not row:raise learning.LearningError(404,"Không tìm thấy câu hỏi.")
                if row.get("response_type") == "file":
                    if form.get("target_type") == "assignment":
                        return question_library.assign_files(session, {**form, "question_ids":json.dumps([row["id"]])}, ip)
                    raise learning.LearningError(400, "Câu hỏi nộp file: dùng Tạo đề thi độc lập để ghép thành đề thi.")
                destination=learning.text(form,"course_id",80)
                permissions.require_course(session,destination)
                learning.course_access(learning.load(),destination,session,write=True)
                kind=form.get("target_type")
                config=copy.deepcopy(row["programming"])
                if form.get("target_id"):
                    if kind not in {"assignment","exam"}:raise learning.LearningError(400,"Chỉ thêm câu hỏi vào bài tập hoặc đề thi.")
                    targets,draft=target(kind,form["target_id"],session)
                    if draft.get("course_id")!=destination:raise learning.LearningError(400,"Nội dung đích không thuộc khóa học đã chọn.")
                    if draft.get("state")!="idle" or not draft.get("programming"):
                        raise learning.LearningError(409,"Chỉ thêm câu hỏi vào bản nháp lập trình chưa giao/mở thi.")
                    languages=[l for l in draft["programming"]["languages"] if l in config["languages"]]
                    if not languages or not set(draft.get("classification_languages",[])).issubset(languages):
                        raise learning.LearningError(400,"Ngôn ngữ câu hỏi không tương thích với nội dung đích.")
                    draft["programming"]=exam_catalog.validate_programming({"languages":",".join(languages),"problems":json.dumps(draft["programming"]["problems"]+config["problems"])})
                    draft["updated_at"]=utc_now()
                    write_json(TARGETS[kind],targets)
                    audit("classification.question-reuse",session["user_id"],ip,{"source_id":row["id"],"target_type":kind,"target_id":draft["id"]})
                    return {"ok":True,"id":draft["id"]}
                # Validate against current limits, even for legacy bank entries.
                fields={**form,"id":"","type":"programming","languages":",".join(config["languages"]),
                        "problems":json.dumps(config["problems"]),"title":form.get("title") or row["title"],
                        "topic_ids":json.dumps(row.get("topic_ids",[])),"difficulty":row.get("difficulty","medium"),
                        "classification_languages":json.dumps(row.get("classification_languages",[]))}
                # Inactive topics remain on the source; new content uses active topics only.
                active={t["id"] for t in read_json("topics.json",[]) if t.get("active",True)}
                fields["topic_ids"]=json.dumps([t for t in row.get("topic_ids",[]) if t in active])
                if kind=="assignment":
                    from . import programming_assignments
                    result=programming_assignments.manage(session,"save",fields,ip)
                elif kind=="exam":
                    fields["assessment_type"]="test"
                    result=exam_catalog.save(session,fields,ip)
                elif kind=="question":
                    config=exam_catalog.validate_programming(fields)
                    clone={**copy.deepcopy(row),"id":"q_"+secrets.token_hex(12),"course_id":destination,
                           "created_by":session["user_id"],"created_at":utc_now(),"published":False,
                           "programming":config,"source_question_id":row["id"]}
                    clone.update(metadata(fields))
                    rows.append(clone);write_json("questions.json",rows)
                    result={"ok":True,"id":clone["id"]}
                else:raise learning.LearningError(400,"Loại nội dung đích không hợp lệ.")
                audit("classification.question-reuse",session["user_id"],ip,{"source_id":row["id"],"target_type":kind,"target_id":result["id"]})
                return result
            if action=="question-save":
                if row and row.get("published"):raise learning.LearningError(409,"Câu hỏi đã công bố, cần tạo bản mới để bảo toàn phiên bản.")
                kind_meta=question_library.question_metadata(form,row)
                if kind_meta["response_type"] == "code":
                    config=exam_catalog.validate_programming(form)
                    if len(config["problems"])!=1 or not config["problems"][0]["tests"]:raise learning.LearningError(400,"Câu hỏi cần đúng một bài toán có test case.")
                else:
                    extensions=list(dict.fromkeys(form.get("file_extensions", ".pdf .zip .txt").lower().split()))
                    if not extensions or any(e not in learning.EXTENSIONS for e in extensions):raise learning.LearningError(400,"Định dạng bài nộp không hợp lệ.")
                    file_question={"statement":learning.text(form,"file_statement",20000),"extensions":extensions,
                                   "points":exam_catalog.integer(form.get("file_points",100),"Điểm câu hỏi",1,1000)}
                if row is None:
                    row={"id":"q_"+secrets.token_hex(12),"created_at":utc_now(),"created_by":session["user_id"],"course_id":course_id,"published":False};rows.append(row)
                row.update(**kind_meta,**metadata(form,row))
                if kind_meta["response_type"] == "code":
                    row.update(title=config["problems"][0]["title"],programming=config)
                    row.pop("file_question",None)
                else:
                    row.update(title=learning.text(form,"file_title"),file_question=file_question)
                    row.pop("programming",None)
                validate_languages(row)
            elif not row:raise learning.LearningError(404,"Không tìm thấy câu hỏi.")
            elif action=="question-publish":row["published"]=True
            elif action=="question-archive":row["archived"]=True
            else:raise learning.LearningError(400,"Thao tác không hợp lệ.")
            row["content_type"]="question";row["updated_at"]=utc_now();write_json("questions.json",rows)
            question_library.sync_file_practice(row)
        else:
            raise learning.LearningError(400,"Thao tác không hợp lệ.")
        details={"id":form.get("id"),"course_id":form.get("course_id")}
        if action=="course-teachers":details["teacher_ids"]=ids
        audit("classification."+action,session["user_id"],ip,details)
        if action=="course-teachers":
            return {"ok":True,"course_id":course["id"],"teacher_ids":list(course["teacher_ids"])}
        return {"ok":True}
