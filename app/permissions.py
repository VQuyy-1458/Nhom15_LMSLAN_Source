"""Default-deny role + course + owner authorization shared by HTTP and services."""
from .storage import read_json


def deny(message="Bạn không có quyền quản lý nội dung này."):
    from .learning import LearningError
    raise LearningError(403, message)


def staff(session):
    return session.get("role") in {"admin", "teacher"}


def course_allowed(session, course_id):
    if session.get("role") == "admin":
        return True
    from .learning import load
    course = next((c for c in load()["courses"] if c["id"] == course_id), None)
    if not course:
        return False
    if session.get("role") == "teacher":
        return session["user_id"] in course.get("teacher_ids", [])
    return course.get("student_ids") is None or session["user_id"] in course["student_ids"]


def manages(session, row):
    return session.get("role") == "admin" or (session.get("role") == "teacher" and row.get("created_by") == session["user_id"] and course_allowed(session, row.get("course_id")))


def require_content(session, row):
    if not manages(session, row):
        deny()
    return row


def require_course(session, course_id):
    if not staff(session) or not course_allowed(session, course_id):
        deny("Bạn không được phân công quản lý khóa học này.")


def exam_row(item_id):
    from . import programming_assignments, exam_catalog
    from .question_library import practice_rows
    return next((r for r in programming_assignments.listing()+exam_catalog.listing()+practice_rows() if r["id"] == item_id), {})


def submission_parent(row):
    if row.get("exam_id"):
        return exam_row(row["exam_id"])
    from .learning import load
    return next((a for a in load()["assignments"] if a["id"] == row.get("assignment_id")), {})


def authorize_route(session, req, resource=True):
    """Only deliberately supported management endpoints are available to teachers."""
    if session["role"] == "admin":
        return
    if session["role"] != "teacher":
        deny()
    path, form = req.path, req.form
    query = lambda key: req.query.get(key, [""])[0]
    if path in {"/admin", "/admin/dashboard", "/admin/calendar", "/admin/class-notifications", "/admin/courses", "/admin/exam", "/admin/learning", "/admin/classification", "/admin/submissions"}:
        section = query("section") or ("dashboard" if path == "/admin" else path.rsplit("/",1)[-1])
        if section not in {"dashboard", "calendar", "class-notifications", "courses", "exam", "learning", "classification", "submissions"}:
            deny()
        if query("course") and not course_allowed(session, query("course")):
            deny()
        if query("exam"):
            require_content(session, exam_row(query("exam")))
        return
    if path == "/api/admin/workspace":
        if query("course"):
            require_course(session, query("course"))
        return
    if path.startswith("/api/admin/papers/") or path == "/api/admin/questions/assign-files":
        return  # Service verifies paper ownership and target course.
    if path in {"/api/admin/classification", "/api/admin/classification/assign", "/api/admin/questions/save", "/api/admin/questions/clone", "/api/admin/questions/publish", "/api/admin/questions/reuse", "/api/admin/questions/archive"}:
        return  # Target-specific checks are performed by the classification service.
    if path.startswith("/api/admin/archive/"):
        if path.rsplit("/",1)[-1] not in {"list","detail","csv","zip","download","preview","view","grade"}:
            deny()
        if resource and (query("id") or form.get("id")):
            from .submission_archive import find
            row = find(query("id") or form.get("id"))
            require_content(session, submission_parent(row["_row"]))
        return
    if path == "/api/admin/exam-configurations/save":
        if resource:
            if form.get("type") != "programming":
                parent=exam_row(form.get("id")) if form.get("id") else {}
                if not (form.get("blueprint_id") or parent.get("blueprint_id")):
                    deny("Đề nộp file của giáo viên cần được tạo từ đề thi độc lập thuộc quyền quản lý.")
            require_course(session, form.get("course_id"))
            if form.get("id"):
                require_content(session, exam_row(form["id"]))
            validate_roster(session, form.get("participant_ids", ""))
        return
    allowed = {"/api/admin/programming-assignments/save", "/api/admin/programming-assignments/assign", "/api/admin/programming-assignments/delete",
               "/api/admin/programming/status", "/api/admin/programming/submissions", "/api/admin/programming/participants", "/api/admin/programming/control", "/api/admin/programming/rejudge",
               "/api/admin/exam-preflight", "/api/admin/exam-preflight/verify", "/api/admin/exam-preflight/open", "/api/admin/exam-timing"}
    if path not in allowed:
        deny("Chức năng quản trị hệ thống chỉ dành cho Admin.")
    if not resource:
        return
    item_id = form.get("exam_id") or form.get("id") or query("exam")
    if form.get("submission_id"):
        from .programming import rows
        row = next((r for r in rows() if r["id"] == form["submission_id"]), {})
        require_content(session, submission_parent(row))
    elif item_id:
        require_content(session, exam_row(item_id))
    elif path.endswith("/save"):
        require_course(session, form.get("course_id"))
    elif not path.endswith("/status"):
        deny()
    validate_roster(session, form.get("student_ids", ""))


def validate_roster(session, value):
    if session.get("role") == "teacher":
        ids = value.replace(",", " ").split()
        if any(sid not in read_json("students.json") for sid in ids):
            deny("Giáo viên không được tạo tài khoản mới qua danh sách giao bài/dự thi.")


def learning_action(session, action, form, data):
    if session.get("role") != "teacher":
        return
    from .learning import find
    if action in {"material","assignment","event","schedule-generate"}:
        require_course(session, form.get("course_id"))
        return
    key = {"session-content-save":("events","event_id"), "attendance":("events","event_id"),
           "close-attendance":("attendance","session_id"), "attendance-record":("attendance","session_id"), "grade":("submissions","submission_id")}.get(action)
    if not key:
        deny()
    row = find(data,key[0],form.get(key[1]))
    if action == "grade":
        row = submission_parent(row)
    require_content(session,row)
