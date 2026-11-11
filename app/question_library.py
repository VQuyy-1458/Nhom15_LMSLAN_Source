"""Question purposes, reusable papers, practice access and per-student code papers."""
import copy
import json
import secrets
import random
import math
import itertools

from . import learning, permissions
from .storage import read_json, write_json, utc_now, atomic_transaction, audit

PURPOSES = {"practice": "Luyện tập", "practical": "Thực hành", "exam": "Thi"}
FORMATS = {"code": "Code", "file": "Nộp file"}


def question_metadata(form, old=None):
    old = old or {}
    purpose = form.get("purpose", old.get("purpose", "exam"))
    response = form.get("response_type", old.get("response_type", "code"))
    if purpose not in PURPOSES or response not in FORMATS:
        raise learning.LearningError(400, "Mục đích hoặc hình thức câu hỏi không hợp lệ.")
    return {"purpose": purpose, "response_type": response}


def select(session, ids, response="code"):
    bank = {q["id"]: q for q in read_json("questions.json", [])}
    rows = []
    for qid in ids:
        q = bank.get(qid)
        if not q:
            raise learning.LearningError(404, "Không tìm thấy câu hỏi.")
        permissions.require_content(session, q)
        if q.get("archived"):
            raise learning.LearningError(409, "Câu hỏi đã lưu trữ.")
        if q.get("response_type", "code") != response:
            raise learning.LearningError(400, "Câu hỏi không đúng hình thức của đề.")
        rows.append(q)
    return rows


def merge_code(session, form):
    """Resolve selected bank IDs on the server; never trust client test snapshots."""
    from .classification import values
    ids = values(form, "question_ids", [])
    if not ids:
        return dict(form)
    try:
        problems = json.loads(form.get("problems", "[]"))
    except (ValueError, TypeError):
        raise learning.LearningError(400, "Danh sách bài toán không hợp lệ.")
    if not isinstance(problems, list):
        raise learning.LearningError(400, "Danh sách bài toán không hợp lệ.")
    for q in select(session, ids):
        if not set(form.get("languages", "").split(",")).issubset(q["programming"]["languages"]):
            raise learning.LearningError(400, "Các câu hỏi không có ngôn ngữ chạy tương thích.")
        problems.extend({**copy.deepcopy(p), "source_question_id": q["id"]} for p in q["programming"]["problems"])
    return {**form, "problems": json.dumps(problems)}


def sync_file_practice(question):
    """Use existing file-submission/history/marking APIs; exclude practice from grades."""
    data = learning.load()
    item_id = "practice_" + question["id"]
    old = next((a for a in data["assignments"] if a["id"] == item_id), None)
    active = (question.get("purpose") == "practice" and question.get("response_type") == "file"
              and question.get("published") and not question.get("archived"))
    if active:
        row = {"id": item_id, "course_id": question["course_id"], "created_by": question["created_by"],
               "created_at": question["created_at"], "title": question["title"],
               "description": question["file_question"]["statement"], "topic": "Luyện tập",
               "practice": True, "published": True, "archived": False, "due_at": "2099-12-31T23:59:59+00:00",
               "max_attempts": 20, "accepted_extensions": question["file_question"]["extensions"],
               "source_question_id": question["id"]}
        if old: old.update(row)
        else: data["assignments"].append(row)
    elif old:
        old["archived"] = True
    if active or old:
        write_json("learning.json", data)


def practice_rows(sid=None):
    rows = []
    for q in read_json("questions.json", []):
        if q.get("purpose") != "practice" or q.get("response_type", "code") != "code" or not q.get("published") or q.get("archived"):
            continue
        course = next((c for c in learning.load()["courses"] if c["id"] == q["course_id"]), None)
        if not course or (sid and course["status"] == "completed"):
            continue
        students = read_json("students.json")
        members = [s for s, r in students.items() if r.get("active", True) and (course.get("student_ids") is None or s in course["student_ids"])]
        if sid and sid not in members:
            continue
        rows.append({**copy.deepcopy(q), "id": "practice_" + q["id"], "type": "programming",
                     "practice": True, "activity_type": "assignment", "assessment_type": "practice",
                     "state": "started", "participants": members, "duration_minutes": 0,
                     "due_at": "2099-12-31T23:59:59+00:00", "ends_at": "2099-12-31T23:59:59+00:00",
                     "description": "Bài tự luyện, không tính vào điểm khóa học."})
    return rows


def papers(session):
    if not permissions.staff(session):permissions.deny()
    return [p for p in read_json("exam_blueprints.json", []) if not p.get("archived") and permissions.manages(session, p)]


def paper(session, item_id):
    row = next((p for p in read_json("exam_blueprints.json", []) if p["id"] == item_id), None)
    if not row:
        raise learning.LearningError(404, "Không tìm thấy đề thi độc lập.")
    permissions.require_content(session, row)
    if row.get("archived") or not row.get("published"):
        raise learning.LearningError(409, "Chỉ sử dụng đề thi đã công bố và chưa lưu trữ.")
    return copy.deepcopy(row)


def manage_paper(session, action, form, ip):
    from . import classification, exam_catalog
    if not permissions.staff(session):permissions.deny()
    with learning.LOCK, atomic_transaction():
        rows = read_json("exam_blueprints.json", [])
        old = next((p for p in rows if p["id"] == form.get("id")), None)
        if form.get("id") and not old:raise learning.LearningError(404, "Không tìm thấy đề thi.")
        if old:permissions.require_content(session, old)
        course = old["course_id"] if old else learning.text(form, "course_id", 80)
        permissions.require_course(session, course)
        learning.course_access(learning.load(), course, session, write=True)
        if action == "save":
            if old and old.get("published"):raise learning.LearningError(409, "Đề đã công bố; hãy tạo bản sao để sửa.")
            response = form.get("response_type", "code")
            if response not in FORMATS:raise learning.LearningError(400, "Hình thức không hợp lệ.")
            ids = classification.values(form, "question_ids", [])
            if not 1 <= len(ids) <= 30:raise learning.LearningError(400, "Chọn từ 1 đến 30 câu hỏi.")
            questions = select(session, ids, response)
            row = {"id": old["id"] if old else "paper_" + secrets.token_hex(12), "course_id": course,
                   "title": learning.text(form, "title"), "response_type": response, "question_ids": ids,
                   "created_by": old["created_by"] if old else session["user_id"],
                   "created_at": old["created_at"] if old else utc_now(), "published": False, "updated_at": utc_now()}
            if response == "code":
                languages = [l for l in classification.LANGUAGES if all(l in q["programming"]["languages"] for q in questions)]
                row["programming"] = exam_catalog.validate_programming(merge_code(session, {"languages": ",".join(languages), "question_ids": json.dumps(ids)}))
                for p, q in zip(row["programming"]["problems"], questions):p["source_question_id"] = q["id"]
            else:
                row["file_questions"] = [{"id": q["id"], "title": q["title"], **copy.deepcopy(q["file_question"])} for q in questions]
            rows = [p for p in rows if p["id"] != row["id"]] + [row]
        elif not old:raise learning.LearningError(404, "Không tìm thấy đề thi.")
        elif action == "publish":old["published"] = True;row = old
        elif action == "archive":old["archived"] = True;row = old
        elif action == "clone":
            row = {**copy.deepcopy(old), "id": "paper_" + secrets.token_hex(12), "published": False,
                   "archived": False, "created_at": utc_now(), "title": old["title"] + " (bản sao)", "created_by": session["user_id"]}
            rows.append(row)
        else:raise learning.LearningError(400, "Thao tác không hợp lệ.")
        write_json("exam_blueprints.json", rows)
        audit("paper." + action, session["user_id"], ip, {"id": row["id"]})
        return {"ok": True, "id": row["id"]}


def assign_files(session, form, ip):
    from .classification import values
    permissions.require_course(session, form.get("course_id"))
    with learning.LOCK, atomic_transaction():
        questions = select(session, values(form, "question_ids", []), "file")
        if not questions:raise learning.LearningError(400, "Hãy chọn câu hỏi nộp file.")
        description = "\n\n".join(f"Câu {i+1}. {q['title']} ({q['file_question']['points']} điểm)\n{q['file_question']['statement']}" for i, q in enumerate(questions))
        result = learning.mutate(session, "assignment", {**form, "description": description}, {}, ip)
        data = learning.load()
        row = next(a for a in data["assignments"] if a["id"] == result["id"])
        row.update(purpose="practical", source_question_ids=[q["id"] for q in questions],
                   accepted_extensions=sorted({e for q in questions for e in q["file_question"]["extensions"]}))
        write_json("learning.json", data)
        return result


def assigned_indices(row, sid):
    if row.get("paper_distribution") == "random":
        return list(row.get("student_problem_sets", {}).get(sid, []))
    return list(range(len(row.get("programming", {}).get("problems", []))))


def allocate(row, participants):
    if row.get("paper_distribution") != "random":return
    size = len(row["programming"]["problems"])
    count = int(row["questions_per_student"])
    if not 1 <= count <= size:raise learning.LearningError(400, "Số câu mỗi sinh viên phải nằm trong số câu của đề.")
    sets = row.setdefault("student_problem_sets", {})
    rng = random.SystemRandom()
    used={tuple(indices) for sid,indices in sets.items() if sid in participants}
    combinations=math.comb(size,count)
    for sid in participants:
        if sid not in sets:
            chosen=tuple(sorted(rng.sample(range(size),count)))
            if len(used)<combinations:
                for _ in range(30):
                    if chosen not in used:break
                    chosen=tuple(sorted(rng.sample(range(size),count)))
                if chosen in used:chosen=next(c for c in itertools.combinations(range(size),count) if c not in used)
            sets[sid]=list(chosen);used.add(chosen)
    row["student_problem_sets"] = {s: sets[s] for s in participants}


def file_control(session, form, ip):
    from . import exam_catalog, exams
    with learning.LOCK, atomic_transaction():
        row=next((r for r in exam_catalog.listing() if r["id"]==form.get("exam_id")),None)
        if not row:raise learning.LearningError(404,"Không tìm thấy kỳ thi.")
        permissions.require_content(session,row)
        learning.course_access(learning.load(),row["course_id"],session,write=True)
        if row["type"]!="file" or not row.get("generated_exam_file"):
            raise learning.LearningError(400,"Chỉ vận hành đề file được tạo từ ngân hàng tại đây.")
        action=form.get("action")
        if action=="distribute":
            if row["state"]!="idle":raise learning.LearningError(409,"Đề đã được phân phối hoặc kỳ thi đã mở.")
            exam_catalog.activate(session,{"id":row["id"]},ip)
            settings=read_json("settings.json")
            ids=list(dict.fromkeys(form.get("student_ids","").replace(","," ").split()))
            if ids:
                permissions.validate_roster(session," ".join(ids))
                allowed=set(settings["exam_participants"])
                if not set(ids).issubset(allowed):raise learning.LearningError(403,"Sinh viên không thuộc khóa học.")
                settings["exam_participants"]=ids;write_json("settings.json",settings)
            result=exams.distribute_exams("selected",{"exam_files":[row["generated_exam_file"]]})
        elif action=="start":
            if read_json("settings.json").get("exam_catalog_id")!=row["id"]:raise learning.LearningError(409,"Kỳ thi chưa được phân phối.")
            try:exams.start_exam_session(actor=session["user_id"])
            except ValueError as error:raise learning.LearningError(409,str(error))
            result={"ok":True}
        elif action=="end":
            settings=read_json("settings.json")
            if settings.get("exam_catalog_id")!=row["id"] or settings.get("exam_state")!="started":raise learning.LearningError(409,"Kỳ thi không đang mở.")
            ended=utc_now();settings.update(exam_state="ended",exam_released=False,exam_ends_at=ended,exam_ended_at=ended)
            write_json("settings.json",settings)
            assignments=read_json("assignments.json")
            for item in assignments.values():
                if item.get("release_id")==settings.get("exam_release_id"):
                    item.setdefault("closed_at",ended);item["ends_at"]=ended
                    if item.get("status")!="submitted":item["status"]="ended"
            write_json("assignments.json",assignments);result={"ok":True}
        else:raise learning.LearningError(400,"Thao tác không hợp lệ.")
        audit("paper.file-"+action,session["user_id"],ip,{"exam_id":row["id"]})
        return result
