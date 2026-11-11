"""Independent homework using the shared programming submission and judge engine."""
import copy
import json
import secrets
import threading
from datetime import datetime, timezone

from . import learning, exam_catalog, code_runner, submission_rate
from .storage import read_json, write_json, atomic_transaction, utc_now, audit

STORE = "programming_assignments.json"
_runs = threading.BoundedSemaphore(2)


def listing():
    return read_json(STORE, [])


def find(item_id):
    item = next((r for r in listing() if r["id"] == item_id), None)
    if not item:
        raise learning.LearningError(404, "Không tìm thấy bài tập lập trình.")
    return item


def manage(session, action, form, ip):
    from . import permissions, classification
    if not permissions.staff(session):
        raise learning.LearningError(403, "Chỉ giảng viên được quản lý bài tập.")
    with learning.LOCK, atomic_transaction():
        items = listing()
        old = next((r for r in items if r["id"] == form.get("id")), None)
        if form.get("id") and not old:
            raise learning.LearningError(404, "Không tìm thấy bài tập lập trình.")
        if action != "save" and not old:
            raise learning.LearningError(404, "Không tìm thấy bài tập lập trình.")
        course_id = old["course_id"] if old else learning.text(form, "course_id", 80)
        permissions.require_course(session,course_id)
        if old: permissions.require_content(session,old)
        course = learning.course_access(learning.load(), course_id, session, write=True)
        if action == "save":
            if old and old["state"] != "idle":
                raise learning.LearningError(409, "Bài đã giao, không thể thay đổi đề và test case.")
            due = learning.date_value(form.get("due_at"))
            if due <= datetime.now(timezone.utc):
                raise learning.LearningError(400, "Hạn nộp phải ở tương lai.")
            from .question_library import merge_code
            form = merge_code(session, form)
            config = exam_catalog.validate_programming(form)
            known={p.get("source_question_id") for p in (old or {}).get("programming",{}).get("problems",[])}
            known.update(classification.values(form,"question_ids",[]))
            for problem,raw in zip(config["problems"],json.loads(form.get("problems","[]"))):
                if isinstance(raw.get("source_question_id"),str) and raw["source_question_id"] in known:problem["source_question_id"]=raw["source_question_id"]
            if not config["problems"] or any(not p["tests"] for p in config["problems"]):
                raise learning.LearningError(400, "Cần ít nhất một bài toán và test case cho mỗi bài.")
            row = {"id": old["id"] if old else "pa_" + secrets.token_hex(12),
                   "type": "programming", "activity_type": "assignment", "course_id": course_id,
                   "purpose": "practical",
                   "title": learning.text(form, "title"), "description": learning.text(form, "description", 10000, False),
                   "topic": learning.text(form, "topic", 200, False), "programming": config,
                   "due_at": due.isoformat(), "ends_at": due.isoformat(), "state": "idle", "participants": [],
                   "created_at": old["created_at"] if old else utc_now(), "created_by": old.get("created_by") if old else session["user_id"],
                   "updated_at": utc_now(), "duration_minutes": 0, "assessment_type": "homework"}
            row.update(classification.metadata(form,old),content_type="assignment")
            classification.validate_languages(row)
            items = [r for r in items if r["id"] != row["id"]] + [row]
        elif action == "assign":
            if old["state"] != "idle":
                raise learning.LearningError(409, "Bài tập đã được giao.")
            if learning.date_value(old["due_at"]) <= datetime.now(timezone.utc):
                raise learning.LearningError(409, "Bài tập đã hết hạn nộp.")
            students = read_json("students.json")
            members = {sid for sid in students if course.get("student_ids") is None or sid in course["student_ids"]}
            ids = list(dict.fromkeys(form.get("student_ids", "").replace(",", " ").split()))
            if not ids or not set(ids).issubset(members) or any(not students[s].get("active", True) for s in ids):
                raise learning.LearningError(400, "Chọn học viên đang hoạt động và thuộc khóa học.")
            old.update(state="started", participants=ids, started_at=utc_now(), assigned_at=utc_now())
            row = old
        elif action == "delete":
            if old["state"] != "idle":
                raise learning.LearningError(409, "Chỉ xóa bản nháp, giữ nguyên lịch sử bài đã giao.")
            items = [r for r in items if r["id"] != old["id"]]
            row = old
        else:
            raise learning.LearningError(400, "Thao tác không hợp lệ.")
        write_json(STORE, items)
        audit("programming.assignment_" + action, session["user_id"], ip, {"id": row["id"]})
        return {"ok": True, "id": row["id"], "state": row["state"], "participant_count": len(row["participants"])}


def run_sample(session, form, ip):
    """Run public samples or custom input without creating a scored submission."""
    from . import programming
    with learning.LOCK:
        row, problem = programming.writable_problem(session["user_id"], form)
        language, source = form.get("language"), form.get("source", "")
        if language not in row["programming"]["languages"]:
            raise learning.LearningError(400, "Ngôn ngữ không được phép.")
        if not source.strip() or len(source.encode("utf-8")) > 100000:
            raise learning.LearningError(400, "Mã nguồn phải từ 1 đến 100.000 byte.")
        problem = copy.deepcopy(problem)
        custom = form.get("run_mode", "samples") == "custom"
        if custom:
            value = form.get("stdin", "")
            if len(value.encode("utf-8")) > 100000:
                raise learning.LearningError(400, "Input tối đa 100.000 byte.")
            problem["tests"] = [{"input": value, "output": "", "sample": True}]
        else:
            problem["tests"] = [t for t in problem["tests"] if t["sample"]]
        if not problem["tests"]:
            raise learning.LearningError(400, "Bài chưa có test mẫu. Hãy chọn chạy với input tự nhập.")
    if not code_runner.ready():
        raise learning.LearningError(503, "Bộ chấm Docker chưa sẵn sàng.")
    if not _runs.acquire(blocking=False):
        raise learning.LearningError(429, "Có nhiều lượt chạy thử. Hãy thử lại sau.")
    try:
        with submission_rate.guard(session["user_id"]):
            try:
                result = code_runner.judge(source.encode("utf-8"), language, problem)
            except Exception as error:
                raise learning.LearningError(503, "Môi trường chạy thử gặp lỗi. Hãy thử lại khi bộ chấm sẵn sàng.") from error
        # The temporary result is returned only to its caller; it never enters score/history stores.
        result.pop("score", None)
        if custom:
            for test in result.get("tests", []):
                test.pop("expected", None)
                if test.get("verdict") == "WA":
                    test["verdict"] = "OK"
            if result.get("verdict") == "WA":
                result["verdict"] = "OK"
        return {"ok": True, "mode": "custom" if custom else "samples", "result": result}
    finally:
        _runs.release()


def homework_scores(course_id, sid):
    """Best graded score per problem, each homework normalized to ten points."""
    from . import programming
    records = programming.rows()
    now = datetime.now(timezone.utc)
    scores = []
    for item in listing():
        if item["course_id"] != course_id or item["state"] == "idle" or sid not in item["participants"]:
            continue
        marks = []
        for index, problem in enumerate(item["programming"]["problems"]):
            attempts = [r for r in records if r["exam_id"] == item["id"] and r["student_id"] == sid and r["problem_index"] == index]
            values = [programming.public_submission(r, True)["effective_score"] for r in attempts]
            values = [v for v in values if v is not None]
            marks.append(max(values) if values else 0 if not attempts and learning.date_value(item["due_at"]) <= now else None)
        if all(v is not None for v in marks):
            scores.append(round(10 * sum(marks) / sum(p["points"] for p in item["programming"]["problems"]), 2))
        elif learning.date_value(item["due_at"]) <= now or any(v is not None for v in marks):
            scores.append(None)
    return scores
