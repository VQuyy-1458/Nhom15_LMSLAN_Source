"""Programming exam attempts and asynchronous grading with private test snapshots."""
import copy
import json
import logging
import random
import threading
import uuid
import hashlib
from contextlib import ExitStack
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import code_runner, exam_catalog, learning, submission_rate
from .config import RUNTIME_DIR
from .storage import read_json, write_json, utc_now, audit, atomic_transaction, save_payload, on_rollback, after_commit

FILES = RUNTIME_DIR / "programming-submissions"
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="code-judge")
_scheduled = set()
_schedule_lock = threading.Lock()


def rows():
    return read_json("programming_submissions.json", [])


def assignment_submissions(sid=None, course_ids=None):
    selected = [r for r in rows() if r.get("assignment_id") and (sid is None or r["student_id"] == sid) and (course_ids is None or r["course_id"] in course_ids)]
    return [public_submission(row, admin=sid is None) for row in selected]


def practice_submissions(sid):
    return [public_submission(row) for row in rows() if row.get("practice_question_id") and row["student_id"] == sid]


def exam(exam_id):
    row = next((r for r in exam_catalog.listing() if r["id"] == exam_id and r["type"] == "programming"), None)
    if not row: raise learning.LearningError(404, "Không tìm thấy kỳ thi lập trình.")
    return row


def eligible(row, sid):
    course = learning.load()["courses"]
    c = next((c for c in course if c["id"] == row["course_id"]), None)
    return sid in row["participants"] and (not row["course_id"] or c and (c.get("student_ids") is None or sid in c["student_ids"]))


def assigned_indices(row, attempt=None):
    pool = row["programming"]["problems"]
    indices = attempt.get("problem_indices") if attempt else None
    return indices if isinstance(indices, list) else list(range(len(pool)))


def public_submission(row, admin=False):
    result = copy.deepcopy(row)
    grades = [h.get("result") for h in result.get("grading_history", [])] + [result.get("result")]
    result["effective_score"] = next((g["score"] for g in reversed(grades) if g and g.get("score") is not None), None)
    if not admin:
        for grade in grades:
            if not grade: continue
            for test in grade["tests"]:
                if not test["sample"]:
                    for key in ("input", "test_code", "expected", "actual", "stderr"): test.pop(key, None)
    return result


def snapshot(sid):
    attempts = read_json("programming_attempts.json", {})
    result = []
    now = datetime.now(timezone.utc)
    for row in exam_catalog.listing():
        if row["type"] != "programming" or (row["state"] == "idle" and not row.get("auto_start_ready")) or not eligible(row, sid): continue
        attempt = attempts.get(row["id"] + ":" + sid)
        from .deadlines import exam_end
        common_end = exam_end(row.get("started_at"), row.get("duration_minutes"), row.get("ends_at"))
        finalized = bool(attempt and attempt.get("status") == "submitted")
        allowed = bool(attempt and not finalized and row["state"] == "started" and not row.get("waiting") and learning.date_value(attempt["ends_at"]) > now)
        item = {k: row.get(k) for k in ("id", "title", "description", "course_id", "duration_minutes", "state", "started_at", "scheduled_at")}
        item["assessment_type"] = row.get("assessment_type", "test")
        if row.get("waiting"):
            item["state"] = "scheduled"
            item["started_at"] = row.get("started_at") or row.get("scheduled_at")
        item.update({"ends_at": common_end.isoformat() if common_end else None, "status": "submitted" if finalized else "expired" if (attempt and learning.date_value(attempt["ends_at"])<=now) or (common_end and common_end<=now) else row["state"], "attempt": attempt, "can_start": row["state"] == "started" and not row.get("waiting") and not attempt and (not common_end or common_end>now), "can_submit": allowed and (not common_end or common_end>now), "finalized": finalized, "submitted_at": attempt.get("submitted_at") if finalized else None, "languages": row["programming"]["languages"], "problems": []})
        if attempt:
            item["problems"] = [{"index": i, "title": p["title"], "statement": p["statement"], "points": p["points"], "time_limit_ms": p["time_limit_ms"], "memory_limit_mb": p["memory_limit_mb"], "execution_mode": p.get("execution_mode", "stdin"), "samples": [t for t in p["tests"] if t["sample"]]} for i, real_index in enumerate(assigned_indices(row, attempt)) for p in [row["programming"]["problems"][real_index]]]
        result.append(item)
    return {"exams": result, "submissions": [public_submission(r) for r in rows() if r["student_id"] == sid]}


def control(session, form, ip, runner_ready=None, now=None):
    action = form.get("action")
    if action == "start" and not (code_runner.ready() if runner_ready is None else runner_ready): raise learning.LearningError(409, "Docker/image bộ chấm chưa sẵn sàng. Chạy Docker và tạo image classroom-judge:1 trước.")
    with learning.LOCK, atomic_transaction():
        row = exam(form.get("exam_id"))
        if action == "start":
            if row["state"] != "idle": raise learning.LearningError(409, "Kỳ thi không ở trạng thái bản nháp.")
            problems = row["programming"]["problems"]
            if not problems or any(not p["tests"] for p in problems): raise learning.LearningError(400, "Mỗi bài toán cần ít nhất một test case trước khi mở thi.")
            if any(not code_runner.budget_valid(p) for p in problems): raise learning.LearningError(400, "Cấu hình đề cũ vượt ngân sách chấm. Hãy giảm số test hoặc thời gian mỗi test trước khi mở thi.")
            from .admin_workspace import course_members
            course, members = course_members(row["course_id"])
            if course and course["status"] == "completed": raise learning.LearningError(409, "Khóa học đã tổng kết.")
            students = read_json("students.json")
            if row.get("participants_configured"):
                participants = list(row["participants"])
                if not participants:
                    raise learning.LearningError(400, "Danh sách dự thi đang trống. Hãy lưu danh sách trước khi mở thi.")
                if not set(participants).issubset(members) or any(not students.get(sid, {}).get("active", True) for sid in participants):
                    raise learning.LearningError(409, "Danh sách dự thi có sinh viên không còn thuộc khóa học hoặc tài khoản đã khóa. Hãy cập nhật danh sách trước khi mở thi.")
            else:
                participants = sorted(s for s in members if students[s].get("active", True))
            now = now or datetime.now(timezone.utc)
            from .exam_timing import window
            begins, ends = window(row.get("scheduled_at"), row["duration_minutes"], now)
            if ends <= now:
                raise learning.LearningError(409, "Lịch thi đã hết thời gian. Hãy điều chỉnh giờ bắt đầu trước khi mở.")
            row.update({"state": "started", "started_at": begins.isoformat(), "ends_at": ends.isoformat(), "participants": participants})
        elif action == "end":
            if row["state"] not in {"started", "scheduled"}: raise learning.LearningError(409, "Kỳ thi chưa mở.")
            row.update({"state": "ended", "ended_at": utc_now()})
        else: raise learning.LearningError(400, "Thao tác không hợp lệ.")
        catalog = read_json("exam_catalog.json", [])
        row.pop("active", None)
        catalog = [r for r in catalog if r["id"] != row["id"]] + [row]
        write_json("exam_catalog.json", catalog)
        audit("programming.exam_" + action, session["user_id"], ip, {"exam_id": row["id"]})
        return {"ok": True}


def student_submissions(sid, exam_id, problem_index):
    row = exam(exam_id)
    if not eligible(row, sid): raise learning.LearningError(403, "Bạn không thuộc danh sách dự thi.")
    attempt = read_json("programming_attempts.json", {}).get(row["id"] + ":" + sid)
    index = exam_catalog.integer(problem_index, "Chỉ số bài toán", 0, len(assigned_indices(row, attempt))-1)
    from .deadlines import exam_end
    end = exam_end(row.get("started_at"), row.get("duration_minutes"), row.get("ends_at"))
    now = datetime.now(timezone.utc)
    allowed = bool(attempt and attempt.get("status") != "submitted" and row["state"] == "started" and not row.get("waiting") and learning.date_value(attempt["ends_at"]) > now and (not end or end > now))
    return {"submissions": [public_submission(r) for r in rows() if r["student_id"] == sid and r["exam_id"] == exam_id and r["problem_index"] == index],
            "can_submit": allowed, "server_time": utc_now(), "ends_at": attempt.get("ends_at") if attempt else None}


def start(session, form, ip):
    sid = session["user_id"]
    with learning.LOCK, atomic_transaction():
        row = exam(form.get("exam_id"))
        if not eligible(row, sid): raise learning.LearningError(403, "Bạn không thuộc danh sách dự thi.")
        if row.get("waiting"): raise learning.LearningError(409, "Chưa đến giờ bắt đầu dự kiến của kỳ thi.")
        if row["state"] != "started": raise learning.LearningError(409, "Giảng viên chưa mở hoặc đã kết thúc kỳ thi.")
        from .deadlines import exam_end
        common_end = exam_end(row.get("started_at"), row.get("duration_minutes"), row.get("ends_at"))
        if common_end and common_end<=datetime.now(timezone.utc): raise learning.LearningError(409,"Đã hết thời gian bắt đầu kỳ thi của lớp.")
        attempts = read_json("programming_attempts.json", {})
        key = row["id"] + ":" + sid
        if key not in attempts:
            now = datetime.now(timezone.utc)
            pool = row["programming"]["problems"]
            count = row["programming"].get("question_count", len(pool))
            selected = random.SystemRandom().sample(range(len(pool)), count) if count < len(pool) else list(range(len(pool)))
            attempts[key] = {"started_at": now.isoformat(), "ends_at": (common_end or now + timedelta(minutes=row["duration_minutes"])).isoformat(), "problem_indices": selected}
            write_json("programming_attempts.json", attempts)
            audit("programming.student_started", sid, ip, {"exam_id": row["id"]})
        return {"ok": True}


def finish(session, form, ip):
    """Let a student finalize early and immediately leave monitoring."""
    sid = session["user_id"]
    with learning.LOCK, atomic_transaction():
        row = exam(form.get("exam_id"))
        if not eligible(row, sid):
            raise learning.LearningError(403, "Bạn không thuộc danh sách dự thi.")
        attempts = read_json("programming_attempts.json", {})
        key = row["id"] + ":" + sid
        attempt = attempts.get(key)
        if not attempt:
            raise learning.LearningError(409, "Bạn chưa vào làm bài thi.")
        if attempt.get("status") == "submitted":
            return {"ok": True, "submitted_at": attempt.get("submitted_at")}
        now = datetime.now(timezone.utc)
        if row["state"] != "started" or row.get("waiting") or learning.date_value(attempt["ends_at"]) <= now:
            raise learning.LearningError(409, "Kỳ thi đã hết thời gian nộp bài.")
        submitted_at = utc_now()
        attempt.update({"status": "submitted", "submitted_at": submitted_at})
        attempts[key] = attempt
        write_json("programming_attempts.json", attempts)
        audit("programming.student_finished", sid, ip, {"exam_id": row["id"]})
        return {"ok": True, "submitted_at": submitted_at}


def submit(session, form, file, ip):
    if not file or not file.get("filename"): raise learning.LearningError(400, "Hãy chọn file mã nguồn.")
    content = file["data"]
    if not content or len(content) > 100000: raise learning.LearningError(400, "Mã nguồn phải từ 1 đến 100.000 byte.")
    try: content.decode("utf-8-sig", "strict")
    except UnicodeDecodeError: raise learning.LearningError(400, "Mã nguồn phải dùng UTF-8.")
    sid, language = session["user_id"], form.get("language")
    request_id = form.get("request_id", "").strip()
    if len(request_id) > 80 or any(not (x.isascii() and (x.isalnum() or x in "._:-")) for x in request_id):
        raise learning.LearningError(400, "Mã yêu cầu nộp bài không hợp lệ.")
    runner_ready = code_runner.ready()
    with learning.LOCK, atomic_transaction(), ExitStack() as guards:
        row = exam(form.get("exam_id"))
        if not eligible(row, sid): raise learning.LearningError(403, "Bạn không thuộc danh sách dự thi.")
        attempt = read_json("programming_attempts.json", {}).get(row["id"] + ":" + sid)
        index = exam_catalog.integer(form.get("problem_index"), "Chỉ số bài toán", 0, len(assigned_indices(row, attempt))-1)
        records = rows()
        if request_id:
            previous = next((r for r in records if r["student_id"] == sid and r.get("request_id") == request_id), None)
            if previous:
                if previous["exam_id"] != row["id"] or previous["problem_index"] != index or previous["language"] != language or previous["sha256"] != hashlib.sha256(content).hexdigest():
                    raise learning.LearningError(409, "Yêu cầu gửi lại có nội dung khác. Hãy tạo lần nộp mới.")
                return {"ok":True, "submission":public_submission(previous)}
        if row["state"] != "started" or row.get("waiting") or not attempt or attempt.get("status") == "submitted" or learning.date_value(attempt["ends_at"]) <= datetime.now(timezone.utc): raise learning.LearningError(409, "Chưa bắt đầu, đã nộp bài hoặc đã hết thời gian nộp bài.")
        from .deadlines import exam_end
        common_end = exam_end(row.get("started_at"), row.get("duration_minutes"), row.get("ends_at"))
        if common_end and common_end <= datetime.now(timezone.utc): raise learning.LearningError(409, "Đã hết thời gian nộp bài của kỳ thi.")
        if not runner_ready: raise learning.LearningError(503, "Bộ chấm chưa sẵn sàng, vui lòng thử lại.")
        if language not in row["programming"]["languages"] or language not in code_runner.LANGUAGES: raise learning.LearningError(400, "Ngôn ngữ không được phép trong kỳ thi.")
        if Path(file["filename"]).suffix.lower() != Path(code_runner.LANGUAGES[language]).suffix: raise learning.LearningError(400, "Phần mở rộng file không khớp ngôn ngữ đã chọn.")
        pending = [r for r in records if r["state"] in {"queued", "running"}]
        if len(pending) >= 50 or sum(r["student_id"] == sid for r in pending) >= 2: raise learning.LearningError(429, "Bạn còn bài đang chấm hoặc hàng đợi đang đầy. Chờ kết quả trước khi nộp tiếp.")
        problem = row["programming"]["problems"][assigned_indices(row, attempt)[index]]
        guards.enter_context(submission_rate.guard(sid))
        record = {"id": uuid.uuid4().hex, "exam_id": row["id"], "exam_title": row["title"], "course_id": row["course_id"], "student_id": sid, "problem_index": index, "problem_title": problem["title"], "max_score": problem["points"], "language": language, "original_filename": Path(file["filename"]).name[:150], "submitted_at": utc_now(), "state": "queued", "result": None, "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(), "ip": ip, "grading_history": []}
        record["full_name"] = read_json("students.json").get(sid,{}).get("full_name",sid)
        record["request_id"] = request_id or None
        record["judge_image"] = code_runner.image_identity()
        folder = FILES / record["id"]
        folder.mkdir(parents=True)
        on_rollback(lambda: folder.rmdir())
        save_payload(folder / "source", content)
        save_payload(folder / "problem.json", json.dumps(problem, ensure_ascii=False).encode("utf-8"))
        records.append(record); write_json("programming_submissions.json", records)
        audit("programming.submitted", sid, ip, {"submission_id": record["id"], "exam_id": row["id"]})
        after_commit(lambda: schedule(record["id"]))
    return {"ok": True, "submission": public_submission(record)}


def submit_assignment(session, form, file, ip):
    """Queue a course code exercise through the same isolated judge as exams."""
    language = form.get("language", "")
    if language not in code_runner.LANGUAGES:
        raise learning.LearningError(400, "Ngôn ngữ lập trình không hợp lệ.")
    source = (file or {}).get("data") if file and file.get("filename") else form.get("source", "").encode("utf-8")
    if not source or len(source) > 100000:
        raise learning.LearningError(400, "Mã nguồn phải từ 1 đến 100.000 byte.")
    try:
        source.decode("utf-8-sig", "strict")
    except UnicodeDecodeError:
        raise learning.LearningError(400, "Mã nguồn phải dùng UTF-8.")
    if file and file.get("filename") and Path(file["filename"]).suffix.lower() != Path(code_runner.LANGUAGES[language]).suffix:
        raise learning.LearningError(400, "Phần mở rộng file không khớp ngôn ngữ đã chọn.")
    sid = session["user_id"]
    request_id = form.get("request_id", "").strip()
    if len(request_id) > 80 or any(not (x.isascii() and (x.isalnum() or x in "._:-")) for x in request_id):
        raise learning.LearningError(400, "Mã yêu cầu nộp bài không hợp lệ.")
    with learning.LOCK, atomic_transaction():
        data = learning.load()
        assignment = learning.find(data, "assignments", learning.text(form, "assignment_id", 80))
        learning.course_access(data, assignment["course_id"], session, write=True)
        if assignment.get("kind") != "code":
            raise learning.LearningError(400, "Bài này không nhận mã nguồn.")
        if assignment.get("closed_at") or learning.date_value(assignment["due_at"]) <= datetime.now(timezone.utc):
            raise learning.LearningError(409, "Đã hết hạn nộp bài.")
        records = rows()
        prior = [row for row in records if row.get("assignment_id") == assignment["id"] and row["student_id"] == sid]
        digest = hashlib.sha256(source).hexdigest()
        duplicate = next((row for row in prior if request_id and row.get("request_id") == request_id), None)
        if duplicate:
            if duplicate["sha256"] != digest or duplicate["language"] != language:
                raise learning.LearningError(409, "Yêu cầu gửi lại có nội dung khác.")
            return {"ok": True, "submission": public_submission(duplicate)}
        if len(prior) >= assignment["max_attempts"]:
            raise learning.LearningError(409, "Bạn đã dùng hết số lần nộp bài.")
        if not code_runner.ready():
            raise learning.LearningError(503, "Bộ chấm chưa sẵn sàng, vui lòng thử lại.")
        pending = [row for row in records if row["state"] in {"queued", "running"}]
        if len(pending) >= 50 or sum(row["student_id"] == sid for row in pending) >= 2:
            raise learning.LearningError(429, "Bạn còn bài đang chấm hoặc hàng đợi đang đầy.")
        with submission_rate.guard(sid):
            problem = assignment["problem"]
            record = {"id": uuid.uuid4().hex, "exam_id": "assignment:" + assignment["id"], "assignment_id": assignment["id"], "assignment_title": assignment["title"], "course_id": assignment["course_id"], "student_id": sid, "problem_index": 0, "problem_title": problem["title"], "max_score": problem["points"], "language": language, "original_filename": Path((file or {}).get("filename") or code_runner.LANGUAGES[language]).name[:150], "submitted_at": utc_now(), "state": "queued", "result": None, "size_bytes": len(source), "sha256": digest, "ip": ip, "grading_history": [], "request_id": request_id or None, "attempt": len(prior) + 1, "full_name": read_json("students.json").get(sid, {}).get("full_name", sid), "judge_image": code_runner.image_identity()}
            folder = FILES / record["id"]
            folder.mkdir(parents=True)
            on_rollback(lambda: folder.rmdir())
            save_payload(folder / "source", source)
            save_payload(folder / "problem.json", json.dumps(problem, ensure_ascii=False).encode("utf-8"))
            records.append(record)
            write_json("programming_submissions.json", records)
            audit("programming.assignment_submitted", sid, ip, {"submission_id": record["id"], "assignment_id": assignment["id"]})
            after_commit(lambda: schedule(record["id"]))
    return {"ok": True, "submission": public_submission(record)}


def submit_practice(session, form, ip):
    """Open-ended practice; never contributes to the course gradebook."""
    from . import question_bank
    sid, language = session["user_id"], form.get("language", "")
    if language not in code_runner.LANGUAGES:
        raise learning.LearningError(400, "Ngôn ngữ lập trình không hợp lệ.")
    source = form.get("source", "").encode("utf-8")
    if not source or len(source) > 100000:
        raise learning.LearningError(400, "Mã nguồn phải từ 1 đến 100.000 byte.")
    with learning.LOCK, atomic_transaction():
        question = next((q for q in question_bank.questions() if q["id"] == form.get("question_id")), None)
        if not question or question["kind"] != "code" or question["category"] != "practice" or not question["published"]:
            raise learning.LearningError(404, "Không tìm thấy câu luyện tập đã công khai.")
        learning.course_access(learning.load(), question["course_id"], session)
        if not question["problem"].get("tests"):
            raise learning.LearningError(409, "Câu luyện tập chưa có test case.")
        if not code_runner.ready():
            raise learning.LearningError(503, "Bộ chấm chưa sẵn sàng, vui lòng thử lại.")
        records = rows()
        pending = [row for row in records if row["state"] in {"queued", "running"}]
        if len(pending) >= 50 or sum(row["student_id"] == sid for row in pending) >= 2:
            raise learning.LearningError(429, "Bạn còn bài đang chấm hoặc hàng đợi đang đầy.")
        with submission_rate.guard(sid):
            problem = question["problem"]
            record = {"id": uuid.uuid4().hex, "exam_id": "practice:" + question["id"], "practice_question_id": question["id"], "course_id": question["course_id"], "student_id": sid, "problem_index": 0, "problem_title": problem["title"], "max_score": problem["points"], "language": language, "original_filename": code_runner.LANGUAGES[language], "submitted_at": utc_now(), "state": "queued", "result": None, "size_bytes": len(source), "sha256": hashlib.sha256(source).hexdigest(), "ip": ip, "grading_history": [], "full_name": read_json("students.json").get(sid, {}).get("full_name", sid), "judge_image": code_runner.image_identity()}
            folder = FILES / record["id"]
            folder.mkdir(parents=True)
            on_rollback(lambda: folder.rmdir())
            save_payload(folder / "source", source)
            save_payload(folder / "problem.json", json.dumps(problem, ensure_ascii=False).encode("utf-8"))
            records.append(record)
            write_json("programming_submissions.json", records)
            audit("programming.practice_submitted", sid, ip, {"submission_id": record["id"], "question_id": question["id"]})
            after_commit(lambda: schedule(record["id"]))
    return {"ok": True, "submission": public_submission(record)}


def _work(submission_id):
    try:
        with learning.LOCK, atomic_transaction():
            records = rows(); record = next(r for r in records if r["id"] == submission_id)
            history = record.setdefault("grading_history", [])
            if not history and record.get("result"):
                history.append({"id": "legacy", "result": copy.deepcopy(record["result"]), "graded_at": record.get("graded_at"), "graded_by": "judge"})
            record.update({"state": "running", "stage": "preparing", "result": None}); write_json("programming_submissions.json", records)
        folder = FILES / submission_id
        def progress(stage, completed, total):
            with learning.LOCK, atomic_transaction():
                current = rows()
                item = next(r for r in current if r["id"] == submission_id)
                item.update({"stage": stage, "completed_tests": completed, "total_tests": total})
                write_json("programming_submissions.json", current)
        try:
            result = code_runner.judge((folder / "source").read_bytes(), record["language"], json.loads((folder / "problem.json").read_text(encoding="utf-8")), progress=progress, image=record.get("judge_image"))
            state = "done"
        except Exception:
            logging.getLogger(__name__).exception("Grading failed for submission %s", submission_id)
            result = {"verdict": "SYSTEM_ERROR", "score": None, "passed": 0, "total": 0, "tests": [], "compile_log": "Lỗi môi trường chấm; bài nộp được giữ lại để giảng viên chấm lại."}
            state = "error"
        with learning.LOCK, atomic_transaction():
            records = rows(); record = next(r for r in records if r["id"] == submission_id)
            graded_at = utc_now()
            record.setdefault("grading_history", []).append({"id": uuid.uuid4().hex, "result": copy.deepcopy(result), "graded_at": graded_at, "graded_by": "judge", "requested_by": record.pop("grading_requested_by", None)})
            record.update({"state": state, "stage": state, "result": result, "graded_at": graded_at}); write_json("programming_submissions.json", records)
            audit("programming.graded", "judge", None, {"submission_id": submission_id, "verdict": result["verdict"]})
    finally:
        with _schedule_lock: _scheduled.discard(submission_id)


def schedule(submission_id):
    with _schedule_lock:
        if submission_id not in _scheduled:
            _scheduled.add(submission_id)
            try:
                _pool.submit(_work, submission_id)
            except BaseException:
                _scheduled.discard(submission_id)
                raise


def rejudge(session, form, ip):
    with learning.LOCK, atomic_transaction():
        records = rows(); row = next((r for r in records if r["id"] == form.get("submission_id")), None)
        if not row: raise learning.LearningError(404, "Không tìm thấy bài nộp.")
        if row["state"] in {"queued", "running"}: raise learning.LearningError(409, "Bài đã ở trong hàng đợi chấm.")
        if not row.get("grading_history") and row.get("result"):
            row["grading_history"] = [{"id": "legacy", "result": copy.deepcopy(row["result"]), "graded_at": row.get("graded_at"), "graded_by": "judge"}]
        row["state"] = "queued"; row["stage"] = "queued"; row["completed_tests"] = 0; row["grading_requested_by"] = session["user_id"]; write_json("programming_submissions.json", records)
        audit("programming.rejudge", session["user_id"], ip, {"submission_id": row["id"]})
        after_commit(lambda: schedule(row["id"]))
    return {"ok": True}


def resume():
    for row in rows():
        if row["state"] in {"queued", "running"}: schedule(row["id"])


def shutdown():
    # Leave cancelled queued receipts persisted for the next process to resume.
    # Keep the data lease until the currently running graders have stopped.
    _pool.shutdown(wait=True,cancel_futures=True)
    with _schedule_lock:
        _scheduled.clear()
