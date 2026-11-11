"""Build an isolated, repeat-safe dataset for functional and visual testing."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import time
import zipfile
import zlib
from datetime import datetime, timedelta, timezone

VERSION = "system-test-v1"
PASSWORD = "111111"
PROJECT = Path(__file__).resolve().parents[1]
ADMIN = {"role": "admin", "user_id": "testadmin"}
IP = "127.0.0.1"


def pdf_bytes():
    stream = b"BT /F1 20 Tf 50 750 Td (LAN-LMS - TEST PDF) Tj 0 -35 Td (Sample handout and submission preview.) Tj ET"
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
               b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    result = b"%PDF-1.4\n"
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref = len(result)
    result += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    result += b"".join(f"{n:010} 00000 n \n".encode() for n in offsets[1:])
    return result + f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


def png_bytes():
    width, height = 640, 240
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            color = (36, 94, 219) if 30 < x < 610 and 30 < y < 100 else (237, 244, 255)
            if 30 < x < 380 and 140 < y < 200:
                color = (25, 46, 80)
            row.extend(color)
        rows.append(b"\0" + bytes(row))
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))


def docx_bytes():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml", '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Báo cáo kiểm thử LAN-LMS — tiếng Việt và nội dung nhiều dòng.</w:t></w:r></w:p><w:p><w:r><w:t>Tài liệu mẫu dùng kiểm tra xem trước, tải xuống và nộp bài.</w:t></w:r></w:p></w:body></w:document>')
    return buffer.getvalue()


def create(root):
    from app import storage, learning, seed_demo, exercise_bank, exam_catalog, course_content, question_papers
    from app import programming, notifications, security
    marker = root / "manifest.json"
    if marker.exists():
        result = json.loads(marker.read_text(encoding="utf-8"))
        if result.get("version") != VERSION:
            raise RuntimeError("Dataset version does not match; choose a new --root directory.")
        return result
    if storage.database_path().exists():
        raise RuntimeError("Destination already has a database without a completed manifest. Choose a new --root directory.")
    storage.initialize()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    def iso(days=0, minutes=0):
        return (now + timedelta(days=days, minutes=minutes)).isoformat()
    def mutate(action, **form):
        return learning.mutate(ADMIN, action, {k: str(v) for k, v in form.items()}, {}, IP)["id"]
    def write(name, value):
        storage.write_json(name, value)
    def account(name, **extra):
        return {"full_name": name, "password_hash": security.hash_password(PASSWORD), "active": True,
                "created_at": iso(-30), "created_by": "system-test-fixture", **extra}
    write("admins.json", {"testadmin": account("Quản trị kiểm thử"), "testadmin2": account("Giảng viên thử thao tác")})
    seed_demo.seed_demo(root)
    students = storage.read_json("students.json")
    scenarios = {
        "TESTEMPTY": ("Sinh viên mới — chưa tham gia khóa học", {}),
        "TESTLOCKED": ("Sinh viên bị khóa tài khoản", {"active": False}),
        "TESTTHROTTLE": ("Sinh viên bị khóa đăng nhập tạm", {}),
        "TESTNEWPASS": ("Sinh viên cần đổi mật khẩu lần đầu", {"must_change_password": True}),
        "TESTLONG": ("Nguyễn Thị Hoàng Anh Phương Thảo — Tài khoản kiểm thử tên dài và ký tự tiếng Việt", {}),
        "TESTZERO": ("Sinh viên có điểm 0 hợp lệ", {}),
    }
    for sid, (name, extra) in scenarios.items():
        students[sid] = account(name, student_id=sid, **extra)
    for i in range(21, 46):
        sid = f"DEMO{i:03}"
        students[sid] = account(f"Sinh viên kiểm thử phân trang {i:02}", student_id=sid)
    write("students.json", students)
    write("login_attempts.json", {"testthrottle": {"count": 3, "window_start": time.time(), "locked_until": time.time() + 900}})
    data = learning.load()
    network, database, closed = [c["id"] for c in data["courses"]]
    members = [f"DEMO{i:03}" for i in range(1, 46)] + ["TESTLONG", "TESTZERO", "TESTNEWPASS"]
    data["courses"][0]["student_ids"] = members
    # Seed v1 predates event-linked attendance. Give every session a real lesson.
    statuses = ["present", "late", "early_departure", "absent", "excluded"]
    for i, session in enumerate(data["attendance"]):
        eid = "system-test-lesson-" + session["id"]
        is_open = not session.get("closed")
        lesson = iso(minutes=-5) if is_open else iso(days=-15 + i)
        session.update(event_id=eid, lesson_at=lesson, expires_at=iso(minutes=120) if is_open else iso(days=-14 + i))
        session["records"] = {
            sid: {"status": statuses[j % len(statuses)], "checked_in_at": lesson,
                  "reason": "Dữ liệu mẫu — kiểm tra đầy đủ trạng thái chuyên cần."}
            for j, sid in enumerate(members[:14]) if not is_open or j < 4
        }
        data["events"].append({"id": eid, "course_id": session["course_id"], "title": session["title"],
                               "kind": "lesson", "starts_at": lesson, "location": "Phòng máy QA", "created_at": iso(-20),
                               "description": "Buổi học gắn phiên điểm danh mẫu."})
    # Distinguish zero marks from unpublished/missing marks.
    for component in ("attendance", "homework", "midterm", "final"):
        data["grades"].append({"id": "system-test-zero-" + component, "course_id": network,
                               "student_id": "TESTZERO", "component": component, "score": 0,
                               "created_at": iso(-1), "created_by": ADMIN["user_id"]})
    # Include a genuinely closed task as well as overdue, open and nearly due.
    data["assignments"][1]["closed_at"] = iso(-1)
    data["assignments"][2]["due_at"] = iso(minutes=90)
    write("learning.json", data)
    extra_courses = []
    for i in range(9):
        extra_courses.append(mutate("course", code=f"QA{i+1:02}",
            name=("Khóa học tên rất dài — Lập trình hệ thống phân tán, truyền thông mạng và kiểm thử giao diện trên thiết bị di động" if i == 0 else f"Khóa kiểm thử {i+1:02} · Bộ lọc và phân trang"),
            semester="Học kỳ 1 · 2026–2027" if i % 2 else "Học kỳ 2 · 2025–2026",
            description="Khóa trống dùng thử tạo tài liệu, bài tập, lịch học, điểm danh và cấu hình thi.",
            enrollment="selected", student_ids="DEMO001 TESTLONG" if i < 8 else "DEMO020"))
    inputs = root / "test-inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    payloads = {
        "bao-cao.pdf": pdf_bytes(), "so-do.png": png_bytes(), "bao-cao.docx": docx_bytes(),
        "bai-lam.txt": "Bài nộp kiểm thử LAN-LMS\nHọ tên: Nguyễn Minh Anh\nKiểm tra dấu tiếng Việt, xuống dòng và tải lại tệp.\n".encode(),
        "answer_ac.py": b"a,b=map(int,input().split());print(a+b)\n",
        "answer_wa.py": b"print(0)\n", "answer_ce.cpp": b"int main( { broken syntax\n",
        "answer_tle.py": b"while True: pass\n", "answer_re.py": b"raise RuntimeError('sample runtime error')\n",
        "answer_ac.cpp": b"#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b;}\n",
        "Main.java": b"import java.util.*; public class Main {public static void main(String[] args){Scanner s=new Scanner(System.in);System.out.println(s.nextLong()+s.nextLong());}}\n",
        "import-tai-khoan.txt": "# MSSV|Ngày sinh|Họ tên\nIMPORT001|01012005|Nguyễn Văn Nhập Mẫu\nIMPORT002|02022005|Trần Thị Dữ Liệu\n".encode(),
        "import-tai-khoan-loi.txt": "IMPORT003|03032005|Hợp lệ\nTHIEU_TRUONG\nIMPORT003|04042005|Mã bị lặp\nBAD ID|01012005|Mã sai\n".encode(),
        "testcases.csv": b"input,output,sample\n\"2 3\",5,true\n\"-2 7\",5,false\n\"0 0\",0,false\n",
        "testcases-loi.csv": b"input,output,sample\n2 3,5,not-a-boolean\n",
    }
    payloads["bai-lam.zip"] = seed_demo.zipped({"README.txt": "Bài nộp mẫu, không phải kết quả thật.", "main.py": payloads["answer_ac.py"].decode()})
    payloads["tep-khong-hop-le.exe"] = b"NOT AN EXECUTABLE - invalid extension upload fixture\n"
    payloads["zip-bi-hong.zip"] = b"Not a ZIP archive"
    payloads["bai-lam-rong.txt"] = b""
    for name, payload in payloads.items():
        (inputs / name).write_bytes(payload)
    for i, name in enumerate(["bao-cao.pdf", "so-do.png", "bai-lam.zip", "bai-lam.txt", "bao-cao.docx"]):
        learning.mutate(ADMIN, "material", {"course_id": network, "title": "Xem trước tệp · " + name,
            "description": "Thử xem trước, tải xuống, tên Unicode và kích thước tệp.", "week_number": str(i + 1)},
            {"file": {"filename": name, "data": payloads[name]}}, IP)
    for i in range(15):
        mutate("assignment", course_id=network, title=f"Bài kiểm thử phân trang {i+1:02} · Báo cáo thực hành",
               description="Nộp PDF, TXT hoặc ZIP; thử nộp lại, giới hạn lượt và xem lịch sử.",
               due_at=iso(days=2 + i), max_attempts=3, week_number=i % 6 + 1)
    data = learning.load()
    open_task = next(a for a in data["assignments"] if a["course_id"] == network and a["due_at"] > iso(days=1))
    for attempt in range(3):
        learning.mutate({"role": "student", "user_id": "DEMO004"}, "submit",
            {"assignment_id": open_task["id"], "request_id": f"system-test-limit-{attempt}"},
            {"file": {"filename": f"bao-cao-lan-{attempt+1}.pdf", "data": payloads["bao-cao.pdf"]}}, IP)
    # Reusable code questions, including Java class templates.
    problem = {"title": "Tổng hai số", "statement": "Đọc hai số nguyên a, b (|a|, |b| ≤ 10^9), in a + b.",
               "points": 100, "time_limit_ms": 1000, "memory_limit_mb": 128, "checker": "tokens",
               "tests": [{"input": "2 3\n", "output": "5\n", "sample": True},
                         {"input": "-2 7\n", "output": "5\n", "sample": False},
                         {"input": "1000000000 1000000000\n", "output": "2000000000\n", "sample": False}]}
    questions = []
    for i in range(18):
        form = {"course_id": network, "title": f"Câu mẫu {i+1:02} · Tổng hai số",
                "purpose": ["practice", "practical", "exam"][i % 3], "response_type": "code",
                "languages": "python,cpp,java", "problems": json.dumps([problem]), "week_number": str(i % 6 + 1)}
        qid = exercise_bank.manage_question(ADMIN, "save", form, IP)["id"]
        questions.append(qid)
        if i % 3 == 0:
            exercise_bank.manage_question(ADMIN, "publish", {"id": qid}, IP)
        if i == 17:
            exercise_bank.manage_question(ADMIN, "archive", {"id": qid}, IP)
    java = {"title": "Java OOP · Lớp Product", "statement": "Viết public class Product, constructor Product(long price, int quantity) và long total(). Không viết main/package.",
            "language": "java", "answer_kind": "class", "points": 100, "time_limit_ms": 2000,
            "tests": [{"input": "", "test_code": "System.out.println(new Product(50000L, 2).total());", "output": "100000", "sample": True},
                      {"input": "", "test_code": "System.out.println(new Product(10L, 0).total());", "output": "0", "sample": False}]}
    jq = exercise_bank.manage_question(ADMIN, "save", {"course_id": network, "title": java["title"], "purpose": "practice",
        "response_type": "code", "languages": "java", "problems": json.dumps([java]), "week_number": "2"}, IP)["id"]
    exercise_bank.manage_question(ADMIN, "publish", {"id": jq}, IP)
    (inputs / "Product.java").write_text("public class Product { private long p; private int q; public Product(long price,int quantity){p=price;q=quantity;} public long total(){return p*q;} }\n", encoding="utf-8")
    fq = exercise_bank.manage_question(ADMIN, "save", {"course_id": network, "title": "Báo cáo TCP · Câu hỏi nộp tệp",
        "purpose": "practical", "response_type": "file", "statement": "Trình bày bắt tay TCP ba bước, sơ đồ và ví dụ lỗi kết nối.",
        "extensions": ".pdf .txt .zip", "week_number": "3"}, IP)["id"]
    papers = []
    for i, ids in enumerate([questions[0:2], questions[3:5], [fq]]):
        pid = question_papers.manage(ADMIN, "save", {"title": f"Đề mẫu {i+1:02} · " + ("Nộp file" if i == 2 else "Code"),
            "response_type": "file" if i == 2 else "code", "question_ids": json.dumps(ids)}, IP)["id"]
        question_papers.manage(ADMIN, "publish", {"id": pid}, IP)
        papers.append(pid)
    question_papers.manage(ADMIN, "clone", {"id": papers[0]}, IP)
    archived_paper = question_papers.manage(ADMIN, "clone", {"id": papers[1]}, IP)["id"]
    question_papers.manage(ADMIN, "archive", {"id": archived_paper}, IP)
    practicals = []
    for i, (kind, qids) in enumerate([("code", [questions[1]]), ("file", [fq]), ("file", [fq])]):
        pid = exercise_bank.manage_session(ADMIN, "save", {"course_id": network, "title": ["Thực hành code · Bản nháp để mở", "Thực hành báo cáo · Đang mở", "Thực hành báo cáo · Đã kết thúc"][i],
            "response_type": kind, "question_ids": json.dumps(qids), "duration_minutes": "180", "week_number": "3"}, IP)["id"]
        practicals.append(pid)
        if i:
            exercise_bank.manage_session(ADMIN, "start", {"id": pid, "course_id": network}, IP)
        if i == 2:
            exercise_bank.manage_session(ADMIN, "end", {"id": pid, "course_id": network}, IP)
    exam_ids = []
    for i, (kind, assessment) in enumerate([("file", "test"), ("file", "midterm"), ("file", "final"),
                                          ("programming", "test"), ("programming", "test"), ("programming", "test"), ("programming", "test"), ("programming", "test")]):
        form = {"type": kind, "course_id": network, "title": ["Thi file · Nháp", "Giữa kỳ · Chưa phát đề", "Cuối kỳ · Lịch tuần sau",
                "Code · Nháp mở khi Docker sẵn sàng", "Code · Lịch ngày mai", "Code · Lịch sử kết quả mẫu", "Code · Đã hủy lịch", "Code · Đang mở theo lịch tự động"][i],
                "description": "Dữ liệu kiểm thử. Kết quả lịch sử được dựng sẵn, không phải kết quả chấm thật.",
                "duration_minutes": "180", "assessment_type": assessment,
                "submission_policy": "configurable", "max_submissions": "3", "accepted_submission_extensions": ".pdf .txt .zip"}
        if kind == "programming":
            form.update(languages="python,cpp,java", problems=json.dumps([problem]), participant_ids="\n".join(members))
        if i in (2, 4):
            form["scheduled_at"] = iso(days=7 if i == 2 else 1)
        if i == 7:
            form["scheduled_at"] = iso(minutes=-5)
        exam_ids.append(exam_catalog.save(ADMIN, form, IP)["id"])
    catalog = storage.read_json("exam_catalog.json", [])
    history = next(r for r in catalog if r["id"] == exam_ids[5])
    history.update(state="ended", started_at=iso(-3), ends_at=iso(-3, 180), ended_at=iso(-3, 180))
    next(r for r in catalog if r["id"] == exam_ids[6]).update(state="idle", scheduled_at=None,
        description="Lịch đã hủy; cấu hình trở về bản nháp để giảng viên mở lại.")
    write("exam_catalog.json", catalog)
    attempts, records = {}, []
    verdicts = ["AC", "WA", "CE", "TLE", "MLE", "RE", "SYSTEM_ERROR"]
    for i, verdict in enumerate(verdicts):
        sid = f"DEMO{i+1:03}"
        rid = f"system-test-verdict-{verdict.lower()}"
        source = payloads["answer_ac.py"] if verdict == "AC" else payloads.get(f"answer_{verdict.lower()}.py", payloads["answer_wa.py"])
        folder = programming.FILES / rid
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "source").write_bytes(source)
        (folder / "problem.json").write_text(json.dumps(history["programming"]["problems"][0], ensure_ascii=False), encoding="utf-8")
        result = {"verdict": verdict, "score": 100 if verdict == "AC" else None if verdict == "SYSTEM_ERROR" else 0,
                  "passed": 3 if verdict == "AC" else 0, "total": 3, "tests": [],
                  "compile_log": "[DỮ LIỆU MẪU] Kết quả dựng sẵn để kiểm tra hiển thị, không chạy bộ chấm.", "time_ms": 42, "memory_kb": 2048}
        records.append({"id": rid, "exam_id": history["id"], "exam_title": history["title"], "course_id": network,
            "student_id": sid, "full_name": students[sid]["full_name"], "problem_index": 0, "problem_title": problem["title"],
            "max_score": 100, "language": "python", "original_filename": "fixture-result.py", "submitted_at": iso(-3, 30 + i),
            "state": "error" if verdict == "SYSTEM_ERROR" else "done", "result": result,
            "size_bytes": len(source), "sha256": hashlib.sha256(source).hexdigest(), "ip": IP, "activity_type": "exam",
            "grading_history": [{"id": "sample-initial", "result": result, "graded_at": iso(-3, 40 + i), "graded_by": "fixture"}],
            "fixture": True, "request_id": rid})
        attempts[history["id"] + ":" + sid] = {"started_at": iso(-3, 5), "ends_at": history["ends_at"], "status": "submitted", "submitted_at": iso(-3, 80)}
    write("programming_submissions.json", records)
    write("programming_attempts.json", attempts)
    # Historical file exam submissions, with payloads retained for download/preview.
    file_history = {}
    from app.config import UPLOAD_DIR
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(1, 9):
        sid = f"DEMO{i:03}"
        file_history[sid] = []
        for attempt in range(1, 3):
            filename = f"system-test-{sid}-{attempt}.pdf"
            (UPLOAD_DIR / filename).write_bytes(payloads["bao-cao.pdf"])
            file_history[sid].append({"filename": filename, "original_filename": f"Báo cáo {sid} lần {attempt}.pdf",
                "submitted_at": iso(-5, i + attempt), "release_id": "system-test-old-file-release", "course_id": network,
                "exam_title": "Thi nộp file · Lượt thi lưu trữ", "status": "received", "payload_retained": True,
                "size_bytes": len(payloads["bao-cao.pdf"]), "sha256": hashlib.sha256(payloads["bao-cao.pdf"]).hexdigest()})
    write("submissions.json", file_history)
    # Build weekly content through the same validators as the application.
    data = learning.load()
    code_rows = exercise_bank.code_rows()
    for week in range(1, 7):
        materials = [r["id"] for r in data["materials"] if r["course_id"] == network][(week - 1) % 7:][:2]
        assignments = [r["id"] for r in data["assignments"] if r["course_id"] == network][(week - 1) * 2:week * 2]
        activities = [r["id"] for r in code_rows if r["course_id"] == network and r.get("week_number") == week]
        course_content.save(ADMIN, {"course_id": network, "week_number": str(week), "title": f"Tuần {week:02} · Học liệu và thực hành",
            "lesson_text": "Mục tiêu, nội dung lý thuyết, ví dụ và hướng dẫn làm bài.\nKiểm tra văn bản nhiều dòng và dấu tiếng Việt.",
            "reading_text": "Đọc tài liệu, thử các mẫu mã nguồn trong test-inputs và giữ biên nhận nộp bài.",
            "material_ids": json.dumps(materials), "assignment_ids": json.dumps(assignments),
            "activity_ids": json.dumps(activities), "announcement_ids": "[]"}, IP)
    learning.initialize_enrollments()
    notifications.mark_read("DEMO001", ids=[r["id"] for r in notifications.feed("DEMO001")[:5]])
    settings = storage.read_json("settings.json")
    settings.update(exam_state="started", exam_released=True, exam_started_at=iso(minutes=-5),
                    exam_ends_at=iso(minutes=175), exam_duration_minutes=180)
    write("settings.json", settings)
    assignments = storage.read_json("assignments.json")
    for i, row in enumerate(assignments.values()):
        if i < 3:
            row.update(started_at=iso(minutes=-4), ends_at=settings["exam_ends_at"], status="in_progress")
    write("assignments.json", assignments)
    # Use the real automatic scheduling path; do not stub Docker readiness.
    # The server may open scheduled exams without Docker, but grading still
    # enforces the normal judge readiness check on every real submission.
    from app import exam_schedule, course_packages
    with storage.atomic_transaction():
        exam_schedule.refresh(now)
    package = course_packages.export_course(database, ADMIN)
    (inputs / "khoa-hoc-import.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    (inputs / "khoa-hoc-import-loi.json").write_text('{"format":"wrong-format"}', encoding="utf-8")
    result = {"version": VERSION, "created_at": iso(), "root": str(root), "password": PASSWORD,
              "admin": "testadmin", "student": "DEMO001", "empty_student": "TESTEMPTY",
              "network_course": network, "database_course": database, "completed_course": closed,
              "empty_course": extra_courses[-1], "limit_assignment": open_task["id"], "exam_ids": exam_ids,
              "question_ids": questions + [jq, fq], "paper_ids": papers, "practical_ids": practicals,
              "student_count": len(students), "course_count": len(learning.load()["courses"]),
              "simulated_results": True}
    marker.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "SCENARIOS.md").write_text(
        "# Đường dẫn kiểm thử theo bộ dữ liệu đã tạo\n\n"
        f"Tạo lúc: {now.astimezone(timezone(timedelta(hours=7))).isoformat()}. Mật khẩu mẫu: `{PASSWORD}`.\n\n"
        "Chạy `KIEM_THU_TOAN_BO.bat` từ thư mục gốc. Đăng nhập Admin và sinh viên bằng hai trình duyệt hoặc cửa sổ riêng tư.\n\n"
        "| Tình huống | Đường dẫn / tài khoản |\n|---|---|\n"
        "| Đăng nhập quản trị | http://127.0.0.1:8081/login · `testadmin` |\n"
        f"| Khóa chính, có đủ nội dung | http://127.0.0.1:8081/admin/courses?course={network} |\n"
        f"| Nội dung theo tuần | http://127.0.0.1:8081/student/courses?course={network}&tab=weekly · `DEMO001` |\n"
        f"| Khóa đã tổng kết | http://127.0.0.1:8081/student/courses?course={closed}&tab=grades · `DEMO001` |\n"
        f"| Khóa rỗng | http://127.0.0.1:8081/admin/courses?course={extra_courses[-1]} |\n"
        f"| Đã hết 3 lượt nộp | http://127.0.0.1:8081/student/assignments?course={network} · `DEMO004`, bài `{open_task['title']}` |\n"
        f"| Editor kỳ thi code đang mở | http://127.0.0.1:8081/student/exams?exam={exam_ids[7]} · `DEMO001` |\n"
        f"| Lịch sử code dựng sẵn | http://127.0.0.1:8081/admin?section=exam&exam={exam_ids[5]} |\n"
        "| Điểm 0, tên dài, dữ liệu rỗng | `TESTZERO`, `TESTLONG`, `TESTEMPTY` |\n\n"
        "Tệp nộp, mã nguồn, dữ liệu import hợp lệ/không hợp lệ ở `test-inputs/`.\n"
        "Xem hướng dẫn đầy đủ tại `../FULL_SYSTEM_TEST_GUIDE.md`.\n\n"
        "Thời gian tiếp tục chạy theo server thật: phiên thi khoảng 3 giờ, điểm danh khoảng 2 giờ; "
        "sau đó trở thành trạng thái hết hạn. Muốn một lượt hoàn toàn mới, chạy module với `--root` trỏ một thư mục mới.\n",
        encoding="utf-8")
    return result


def verify(root, baseline=False):
    from app import storage, learning, programming, submission_archive, security, exercise_bank
    from app.config import UPLOAD_DIR
    data = learning.load()
    for key in ("courses", "materials", "assignments", "events", "attendance", "submissions", "grades"):
        rows = data[key]
        assert len({r["id"] for r in rows}) == len(rows), f"Duplicate IDs: {key}"
    courses = {r["id"] for r in data["courses"]}
    for key in ("materials", "assignments", "events", "attendance", "submissions", "grades"):
        assert all(r["course_id"] in courses for r in data[key]), key
    for key in ("materials", "submissions"):
        for row in data[key]:
            if row.get("stored_name"):
                payload = (learning.FILES / row["stored_name"]).read_bytes()
                assert hashlib.sha256(payload).hexdigest() == row["sha256"], row["id"]
    for rows in storage.read_json("submissions.json").values():
        for row in rows:
            assert (UPLOAD_DIR / row["filename"]).is_file()
    for row in programming.rows():
        assert (programming.FILES / row["id"] / "problem.json").is_file()
        assert hashlib.sha256((programming.FILES / row["id"] / "source").read_bytes()).hexdigest() == row["sha256"]
        if row.get("fixture"):
            assert row["state"] not in {"queued", "running"}, "No fake pending jobs may be resumed"
    students = storage.read_json("students.json")
    for sid in ("DEMO001", "TESTEMPTY", "TESTZERO", "TESTLONG", "TESTNEWPASS"):
        if sid not in students:
            assert not baseline, sid
            continue
        if baseline:
            assert security.verify_password(PASSWORD, students[sid]["password_hash"])
        learning.snapshot({"role": "student", "user_id": sid})
        programming.snapshot(sid)
    if baseline:
        assert not learning.snapshot({"role": "student", "user_id": "TESTEMPTY"})["courses"]
        zero = learning.snapshot({"role": "student", "user_id": "TESTZERO"})["gradebooks"]
        assert any(b["items"][0]["total"] == 0 for b in zero)
    archive = submission_archive.listing({})["stats"]
    assert not archive["missing"], archive
    return {"courses": len(data["courses"]), "students": len(students), "assignments": len(data["assignments"]),
            "materials": len(data["materials"]), "attendance": len(data["attendance"]), "submissions": len(data["submissions"]),
            "questions": len(exercise_bank.bank()), "archive": archive}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT / "sample-data" / "full-system")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--check", action="store_true", help="Validate an existing dataset without reseeding")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    root = args.root.resolve()
    if root == PROJECT or root == PROJECT / "data" or PROJECT.is_relative_to(root):
        parser.error("Choose an isolated data directory, not the project's normal runtime root.")
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    os.environ["CSS_DATA_ROOT"] = str(root)
    os.environ["CSS_PORT"] = str(args.port)
    from app.config import DATA_DIR
    from app.runtime import data_lease
    with data_lease(DATA_DIR):
        fresh = not (root / "manifest.json").exists()
        if args.check:
            if not (root / "manifest.json").is_file():
                parser.error("No completed test dataset in this directory")
        else:
            create(root)
        report = verify(root, baseline=fresh)
        (root / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
    if args.serve:
        print(f"TEST DATA: {root}\nURL: http://127.0.0.1:{args.port}\nAdmin: testadmin / {PASSWORD}\nStudent: DEMO001 / {PASSWORD}", flush=True)
        from app.main import main as serve
        serve()


if __name__ == "__main__":
    main()
