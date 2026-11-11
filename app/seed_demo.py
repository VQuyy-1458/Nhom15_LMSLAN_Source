"""Add a separate, repeat-safe classroom dataset. Run with --apply to write it."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import secrets
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config, exams, learning, storage
from .security import hash_password

VERSION = "classroom-demo-v1"
PASSWORD = "111111"
VN = timezone(timedelta(hours=7))
NAMES = ["Nguyễn Minh Anh", "Trần Quốc Bảo", "Lê Minh Châu", "Phạm Thị Duyên", "Hoàng Văn Em", "Võ Ngọc Hà", "Đặng Trung Hiếu", "Bùi Gia Huy", "Đỗ Khánh Linh", "Ngô Hoàng Long", "Nguyễn Thanh Mai", "Trần Hải Nam", "Lê Bảo Ngọc", "Phạm Đức Phúc", "Hoàng Minh Quân", "Võ Phương Thảo", "Đặng Anh Thư", "Bùi Quốc Trung", "Đỗ Ngọc Tú", "Ngô Hải Yến"]


def zipped(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return buffer.getvalue()


ASSIGNMENT_PLANS = {
    "network": [
        "Khảo sát mô hình TCP/IP và công cụ mạng",
        "Xây dựng TCP Echo Client–Server",
        "Giao tiếp UDP và xử lý mất gói",
        "Truyền file an toàn trong mạng LAN",
        "TCP Chat đa luồng",
        "Quản lý nhiều kết nối bằng select",
        "Thiết kế giao thức ứng dụng",
        "WebSocket và trao đổi dữ liệu thời gian thực",
        "Bảo mật kết nối và xác thực người dùng",
        "Đồ án mini Client–Server hoàn chỉnh",
    ],
    "database": [
        "Phân tích yêu cầu và mô hình ERD",
        "Chuẩn hóa dữ liệu đến dạng 3NF",
        "Thiết kế lược đồ và ràng buộc toàn vẹn",
        "Truy vấn JOIN trên nhiều bảng",
        "GROUP BY, HAVING và truy vấn thống kê",
        "Subquery, CTE và truy vấn nâng cao",
        "View, trigger và stored procedure",
        "Giao dịch và xử lý tranh chấp dữ liệu",
        "Tối ưu truy vấn bằng chỉ mục",
        "Đồ án cơ sở dữ liệu ứng dụng",
    ],
    "web": [
        "Xây dựng giao diện responsive",
        "Biểu mẫu và kiểm tra dữ liệu đầu vào",
        "Thiết kế REST API cơ bản",
        "Xác thực và phân quyền người dùng",
        "Kết nối frontend với API",
        "Quản lý trạng thái và xử lý lỗi",
        "Tải file và quản lý tài nguyên",
        "Tìm kiếm, lọc và phân trang",
        "Kiểm thử và tối ưu hiệu năng Web",
        "Đồ án Web full-stack hoàn chỉnh",
    ],
    "programming": [
        "Biến, kiểu dữ liệu và nhập xuất",
        "Cấu trúc rẽ nhánh và vòng lặp",
        "Mảng, chuỗi và xử lý dữ liệu",
        "Hàm và tổ chức chương trình",
        "Con trỏ và quản lý bộ nhớ",
        "Lập trình hướng đối tượng",
        "Đọc ghi file và xử lý ngoại lệ",
        "Cấu trúc dữ liệu cơ bản",
        "Thuật toán tìm kiếm và sắp xếp",
        "Bài tập tổng hợp cuối học phần",
    ],
}


def _assignment_subject(course):
    text = f"{course.get('code', '')} {course.get('name', '')}".casefold()
    if any(token in text for token in ("ltm", "mạng", "network", "socket")):
        return "network"
    if any(token in text for token in ("csdl", "database", "dữ liệu", "sql")):
        return "database"
    if any(token in text for token in ("web", "frontend", "backend")):
        return "web"
    return "programming"


def assignment_metadata(course, index):
    """Return stable list labels for code/file assignments."""
    subject = _assignment_subject(course)
    if subject == "network":
        categories = ["TCP", "TCP", "UDP", "TCP", "TCP", "RMI", "MIXED", "WS", "RMI", "MIXED"]
        codes = ["TCP_TOOLS", "TCP_ECHO", "UDP_RELIABLE", "TCP_FILE", "TCP_CHAT", "IO_SELECT", "APP_PROTOCOL", "WS_REALTIME", "SECURE_LINK", "CLIENT_SERVER"]
    elif subject == "database":
        categories, codes = ["DATABASE"] * 10, ["ERD", "NORMAL_3NF", "SCHEMA", "SQL_JOIN", "SQL_GROUP", "SQL_CTE", "DB_OBJECTS", "TRANSACTION", "SQL_INDEX", "DB_PROJECT"]
    elif subject == "web":
        categories, codes = ["WEB"] * 9 + ["MIXED"], ["RESPONSIVE", "WEB_FORM", "REST_API", "WEB_AUTH", "API_CLIENT", "WEB_STATE", "FILE_UPLOAD", "WEB_FILTER", "WEB_TEST", "FULLSTACK"]
    else:
        categories, codes = ["GENERAL"] * 9 + ["MIXED"], ["BASIC_IO", "CONTROL_FLOW", "ARRAY_STRING", "FUNCTION", "POINTER", "OOP", "FILE_IO", "DATA_STRUCTURE", "ALGORITHM", "FINAL_PRACTICE"]
    pos = index % 10
    return {"submission_type": "file", "category": categories[pos], "short_code": codes[pos]}


def top_up_assignments(per_course=10):
    """Add repeat-safe sample assignments until every course reaches the target."""
    if not isinstance(per_course, int) or not 1 <= per_course <= 50:
        raise ValueError("Số bài mỗi môn phải từ 1 đến 50.")
    data = learning.load()
    now = datetime.now(VN).replace(microsecond=0)
    due_offsets = [2, 4, 7, 10, 14, 18, 23, 28, 34, 42]
    added = []
    updated = 0
    summary = []
    for course in data["courses"]:
        existing = [row for row in data["assignments"] if row.get("course_id") == course["id"]]
        before = len(existing)
        for index, row in enumerate(existing):
            metadata = assignment_metadata(course, index)
            changed = False
            for key, value in metadata.items():
                if (key == "submission_type" and row.get(key) != "file") or not row.get(key) or (row.get("created_by") == "sample-assignment-topup" and row.get(key) != value):
                    row[key] = value
                    changed = True
            if row.get("created_by") == "sample-assignment-topup" and "Nộp mã nguồn hoặc file ZIP" in row.get("description", ""):
                row["description"] = row["description"].replace(
                    "Nộp mã nguồn hoặc file ZIP kèm README hướng dẫn chạy, dữ liệu kiểm thử và ảnh kết quả.",
                    "Nộp báo cáo PDF/DOCX hoặc ZIP tài liệu minh chứng. Phần lập trình có test tự động được làm trong Bộ chấm code online.",
                )
                changed = True
            updated += int(changed)
        titles = {row.get("title", "").strip().casefold() for row in existing}
        plan = ASSIGNMENT_PLANS[_assignment_subject(course)]
        for index, topic in enumerate(plan):
            if len(existing) >= per_course:
                break
            title = f"Bài tập {len(existing)+1:02} · {topic}"
            if title.casefold() in titles:
                continue
            identity = hashlib.sha256(f"{course['id']}:{topic}".encode("utf-8")).hexdigest()[:20]
            assignment_id = "sample-task-" + identity
            if any(row.get("id") == assignment_id for row in data["assignments"]):
                continue
            completed = course.get("status") == "completed"
            offset = -(42 - index * 3) if completed else due_offsets[index]
            due = (now + timedelta(days=offset)).replace(hour=23, minute=59, second=0).astimezone(timezone.utc).isoformat()
            row = {
                "id": assignment_id,
                "course_id": course["id"],
                "title": title,
                "topic": "Thực hành",
                "description": (
                    f"Hoàn thành bài thực hành “{topic}” của môn {course['name']}.\n"
                    "Nộp báo cáo PDF/DOCX hoặc ZIP tài liệu minh chứng. Phần lập trình có test tự động được làm trong Bộ chấm code online.\n"
                    "Tiêu chí: đúng yêu cầu 6 điểm, kiểm thử 2 điểm, trình bày và giải thích 2 điểm."
                ),
                "due_at": due,
                "max_attempts": 5,
                "created_at": now.astimezone(timezone.utc).isoformat(),
                "created_by": "sample-assignment-topup",
                **assignment_metadata(course, index),
            }
            if completed:
                row["closed_at"] = due
            data["assignments"].append(row)
            existing.append(row)
            titles.add(title.casefold())
            added.append(row)
        summary.append({"course_id": course["id"], "code": course.get("code"), "before": before, "after": len(existing)})
    if added or updated:
        with storage.atomic_transaction():
            storage.write_json("learning.json", data)
            storage.audit("setup.sample_assignments_added", "local-user", "127.0.0.1", {"target": per_course, "added": len(added), "updated": updated, "courses": summary})
    return {"target": per_course, "added": len(added), "updated": updated, "courses": summary, "assignment_ids": [row["id"] for row in added]}


def seed_demo(project_root=None):
    root = Path(project_root or config.BASE_DIR)
    if storage.document_exists("demo_seed.json"):
        return {"status": "already-seeded", **storage.read_json("demo_seed.json")}
    now = datetime.now(VN)
    stamp = now.strftime("%Y%m%d-%H%M%S")
    students = storage.read_json("students.json")
    data = learning.load()
    notices = storage.read_json("notifications.json", [])
    settings = storage.read_json("settings.json")
    assignments = storage.read_json("assignments.json")
    ids = [f"DEMO{i:03}" for i in range(1, 21)]
    if any(sid in students for sid in ids) or any(c["id"].startswith("demo-v1-") for c in data["courses"]):
        raise RuntimeError("Có dữ liệu trùng mã DEMO. Không thay đổi dữ liệu đang có.")
    pending_files = {}
    def iso(days=0, hour=None, minute=0):
        value = now + timedelta(days=days)
        if hour is not None:
            value = value.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return value.astimezone(timezone.utc).isoformat(timespec="seconds")
    def identity(key, days=0):
        return {"id": "demo-v1-" + key, "created_at": iso(days), "created_by": "demo-seed"}
    def file_metadata(key, filename, payload):
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        stored = "demo-v1-" + key + Path(filename).suffix
        target = learning.FILES / stored
        if target.exists():
            raise RuntimeError("File mẫu đã tồn tại; không ghi đè: " + str(target))
        pending_files[target] = payload
        return {"original_filename": filename, "stored_name": stored, "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    for index, sid in enumerate(ids):
        students[sid] = {"student_id": sid, "full_name": NAMES[index], "password_hash": hash_password(PASSWORD), "active": True, "created_at": iso(-25), "created_by": "demo-seed", "last_ip": None, "last_seen": None, "must_change_password": False}
    specifications = [
        ("network", "LTM-DEMO-01", "Lập trình mạng", ids[:16], "Thực hành socket, TCP/UDP và ứng dụng Client–Server.", False),
        ("database", "CSDL-DEMO-02", "Cơ sở dữ liệu", ids[8:], "Thiết kế dữ liệu, truy vấn SQL và quản lý giao dịch.", False),
        ("completed", "LT-DEMO-03", "Lập trình căn bản", ids[:8], "Khóa học đã tổng kết để kiểm tra lịch sử, bảng điểm và chế độ chỉ xem.", True),
    ]
    course_ids = []
    task_by_course = {}
    for key, code, name, members, description, completed in specifications:
        course = {**identity(key, -30), "code": code, "name": name, "semester": "Học kỳ 1 · 2026–2027" if not completed else "Học kỳ hè · 2025–2026", "student_ids": members, "description": description, "status": "completed" if completed else "active", "weights": {"attendance": 10, "homework": 20, "midterm": 30, "final": 40}}
        data["courses"].append(course)
        cid = course["id"]
        course_ids.append(cid)
        topics = ["Giới thiệu và thiết lập môi trường", "Cấu trúc chương trình", "Bài tập thực hành", "Xử lý lỗi", "Ôn tập giữa kỳ", "Thực hành tổng hợp"]
        for i in range(6 if completed else 12):
            day = -40 + i * 3 if completed else (-24 + i * 3 if i < 8 else 1 + (i - 8) * 3)
            data["events"].append({**identity(f"{key}-lesson-{i+1}", day), "course_id": cid, "title": f"Buổi {i+1:02}: {topics[i % len(topics)]}", "description": "Chuẩn bị tài liệu và hoàn thành phần thực hành trước buổi học.", "kind": "lesson", "starts_at": iso(day, 7 if key == "network" else 13, 30), "location": "Phòng thực hành A203" if key == "network" else "Phòng thực hành B105"})
        for i in range(3):
            data["events"].append({**identity(f"{key}-notice-{i}", -3+i), "course_id": cid, "title": ["Chào mừng đến với khóa học", "Tài liệu và bài tập đã được cập nhật", "Lưu ý quy định nộp bài"][i], "description": ["Theo dõi lịch học, tài liệu và các hoạt động trong không gian khóa học.", "Xem mục Tài liệu và Bài tập để chuẩn bị cho buổi thực hành tiếp theo.", "Kiểm tra tên file, nội dung và biên nhận sau khi nộp. Liên hệ giảng viên nếu cần hỗ trợ."][i], "kind": "announcement", "starts_at": iso(-3+i), "location": ""})
        material_contents = [
            ("Đề cương học phần", "de-cuong.txt", f"{name}\n\nMục tiêu: {description}\n\nĐánh giá: chuyên cần 10%, bài tập 20%, giữa kỳ 30%, cuối kỳ 40%.\nNộp bài theo hạn quy định và giữ lại biên nhận.\n"),
            ("Hướng dẫn thực hành", "huong-dan.txt", "1. Đọc yêu cầu bài tập.\n2. Hoàn thành báo cáo hoặc tài liệu minh chứng.\n3. Bài lập trình có test tự động được làm trong Bộ chấm code online.\n4. Nộp file và kiểm tra lại lịch sử.\n"),
            ("Mã nguồn tham khảo", "vi-du.cpp", "#include <iostream>\nint main() { int n; std::cin >> n; std::cout << n * (n + 1) / 2; }\n"),
        ]
        for i, (title, filename, payload) in enumerate(material_contents):
            data["materials"].append({**identity(f"{key}-material-{i}", -15+i), "course_id": cid, "title": title, "description": "Học liệu dùng cho bộ dữ liệu kiểm thử của lớp.", **file_metadata(f"{key}-material-{i}", filename, payload)})
        subject = "network" if key == "network" else "database" if key == "database" else "programming"
        titles = [f"Bài tập {i+1:02} – {topic}" for i, topic in enumerate(ASSIGNMENT_PLANS[subject])]
        task_ids = []
        for i, title in enumerate(titles):
            due_day = -50+i*4 if completed else [-10, -3, 3, 7, 12, 18, 24, 31, 39, 48][i]
            task = {**identity(f"{key}-task-{i+1}", -25+i), "course_id": cid, "title": title, "description": f"Hoàn thành nội dung thực hành của {name}.\nNộp báo cáo PDF/DOCX hoặc ZIP tài liệu minh chứng. Bài lập trình có test tự động được làm trong Bộ chấm code online.\nTiêu chí: đúng yêu cầu (6 điểm), kiểm thử (2 điểm), trình bày và hướng dẫn (2 điểm).", "due_at": iso(due_day, 23, 59), "max_attempts": 3, **assignment_metadata(course, i)}
            data["assignments"].append(task)
            task_ids.append(task["id"])
            for j, sid in enumerate(members):
                should_submit = completed or (i == 0 and j % 5 != 4) or (i == 1 and j % 3 != 2) or (i == 2 and j in (2, 3, 5, 7, 9)) or (i == 3 and j in (1, 4))
                if not should_submit:
                    continue
                total_attempts = 2 if not completed and i == 1 and j % 4 == 0 else 1
                for attempt in range(1, total_attempts+1):
                    subkey = f"{key}-task-{i+1}-{sid}-{attempt}"
                    score = round(6 + (j % 8) * .5, 2) if completed or i == 0 or (i == 1 and j % 2 == 0 and attempt == total_attempts) else None
                    payload = zipped({"main.cpp": "#include <iostream>\nint main() { std::cout << \"Hello classroom\"; }\n", "README.txt": f"Bài nộp mẫu: {sid}\n{title}\nLần nộp: {attempt}\nĐây là dữ liệu kiểm thử, không phải kết quả của sinh viên thật.\n"})
                    data["submissions"].append({**identity(subkey, due_day-1 if due_day < 0 else -1), "course_id": cid, "assignment_id": task["id"], "student_id": sid, "attempt": attempt, "request_id": subkey, "score": score, "feedback": "Đã đáp ứng yêu cầu. Cần bổ sung mô tả các tình huống biên." if score is not None else "", **file_metadata(subkey, f"{sid}_BT{i+1:02}_lan{attempt}.zip", payload)})
        task_by_course[cid] = task_ids
        for i in range(6 if completed else 4):
            is_open = not completed and i == 3
            records = {}
            for j, sid in enumerate(members):
                if is_open:
                    if j not in (1, 3, 6):
                        continue
                elif j % 7 == 6:
                    continue
                records[sid] = {"status": "late" if j % 5 == 3 else "present", "checked_in_at": iso(0 if is_open else -20+i*3), "reason": "Bản ghi mẫu để kiểm tra chuyên cần."}
            data["attendance"].append({**identity(f"{key}-attendance-{i}", 0 if is_open else -20+i*3), "course_id": cid, "title": f"Điểm danh buổi {i+1:02}" + (" – Đang mở" if is_open else ""), "description": "Nhập mã hoặc quét QR do giảng viên hiển thị để xác nhận có mặt.", "expires_at": iso(1) if is_open else iso(-19+i*3), "code": secrets.token_hex(4).upper(), "closed": not is_open, "records": records})
        for j, sid in enumerate(members):
            if completed or j < 6:
                for component in (["midterm", "final"] if completed else ["midterm"]):
                    data["grades"].append({**identity(f"{key}-{sid}-{component}", -5), "course_id": cid, "student_id": sid, "component": component, "score": round(6.5 + (j % 6)*.5, 2)})
    for i in range(14):
        notices.append({"id": f"demo-v1-broadcast-{i}", "title": ["Lịch thực hành tuần này", "Nhắc hạn nộp bài", "Hướng dẫn kiểm tra kết quả học tập"][i % 3], "message": ["Các bạn kiểm tra lịch học trong khóa và chuẩn bị tài liệu trước khi đến lớp.", "Bài tập đang mở nhận bài. Kiểm tra hạn nộp, chọn file đúng định dạng và xác nhận biên nhận.", "Điểm và nhận xét của giảng viên được cập nhật trong mục Kết quả học tập."][i % 3], "student_id": ids[i % len(ids)] if i % 4 == 0 else None, "created_at": (now-timedelta(hours=i)).astimezone(timezone.utc).isoformat(timespec="seconds"), "created_by": "Giảng viên"})
    exam_names = ["DEMO_De_Thi_A.txt", "DEMO_De_Thi_B.txt"]
    for i, filename in enumerate(exam_names):
        target = exams.EXAM_DIR / filename
        if target.exists():
            raise RuntimeError("File đề mẫu đã tồn tại; không ghi đè: " + str(target))
        pending_files[target] = (f"KIỂM TRA THỰC HÀNH – ĐỀ {'AB'[i]}\nThời lượng 60 phút.\n\nBài 1 (5 điểm): Viết chương trình tính {'tổng các số chẵn' if i == 0 else 'tổng các số lẻ'} từ 1 đến n.\nBài 2 (5 điểm): Mô tả cách gửi và nhận file qua TCP.\n\nNộp file ZIP gồm mã nguồn và README hướng dẫn chạy. Có thể nộp tối đa 3 lần.\n").encode("utf-8")
    example_payload = zipped({"main.cpp": "#include <iostream>\nint main() { int n; std::cin >> n; int s = 0; for (int i=2;i<=n;i+=2) s+=i; std::cout << s; }\n", "README.txt": "File dùng để thử thao tác nộp bài. Có thể đổi nội dung và nộp lại để xem lịch sử.\n"})
    pending_files[root / "demo-inputs" / "DEMO001_bai_lam.zip"] = example_payload
    exam_ready = settings.get("exam_state") not in {"distributed", "started"} and not settings.get("exam_released")
    if exam_ready:
        release = "demo-v1-release-" + secrets.token_hex(6)
        settings.update({"exam_course_id": course_ids[0], "exam_title": "Kiểm tra thực hành – Bộ dữ liệu mẫu", "exam_state": "distributed", "exam_released": False, "exam_release_id": release, "exam_release_at": iso(), "exam_started_at": None, "exam_participants": ids[:16], "exam_duration_minutes": 60, "submission_policy": "configurable", "max_submissions": 3, "overwrite_previous": False, "accepted_submission_extensions": [".zip", ".txt", ".cpp", ".c", ".java"], "exam_password_enabled": False, "exam_password_hash": None, "distribution_mode": "selected", "distribution_config": {"exam_files": exam_names}})
        for i, sid in enumerate(ids[:16]):
            assignments[sid] = {"exam_file": exam_names[i % 2], "course_id": course_ids[0], "exam_title": settings["exam_title"], "release_id": release, "assigned_at": iso(), "started_at": None, "ends_at": None, "status": "assigned", "ip_at_assignment": None}
    backup = root / "backups" / ("before-demo-" + stamp)
    if backup.exists():
        raise RuntimeError("Thư mục sao lưu đã tồn tại. Hãy chạy lại sau một giây.")
    backup.mkdir(parents=True)
    (backup / "data").mkdir()
    for name in storage.document_names():
        storage.atomic_write(backup / "data" / name, storage.read_json(name))
    written = []
    marker = {"version": VERSION, "created_at": iso(), "backup": str(backup), "students": ids, "courses": course_ids, "primary_assignment": task_by_course[course_ids[0]][2], "exam_ready": exam_ready, "materials_added": 9, "assignments_added": sum(len(rows) for rows in task_by_course.values()), "submissions_added": sum(s["id"].startswith("demo-v1-") for s in data["submissions"])}
    try:
        for path, payload in pending_files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as output:
                output.write(payload)
            written.append(path)
        with storage.atomic_transaction():
            for name, value in [("students.json", students), ("learning.json", data), ("notifications.json", notices)]:
                storage.write_json(name, value)
            if exam_ready:
                storage.write_json("settings.json", settings)
                storage.write_json("assignments.json", assignments)
            storage.write_json("demo_seed.json", marker)
            storage.audit("setup.demo_seeded", "local-user", "127.0.0.1", {"version": VERSION, "backup": str(backup), "exam_ready": exam_ready})
    except Exception:
        for path in written:
            if path.resolve().is_relative_to(root.resolve()):
                path.unlink(missing_ok=True)
        raise
    return {"status": "created", **marker}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Add sample data, with a backup first. Stop the server before running.")
    parser.add_argument("--assignments-per-course", type=int, metavar="N", help="Repeat-safely top up every existing course to N sample assignments.")
    args = parser.parse_args()
    if args.assignments_per_course is not None:
        if not args.apply:
            print(f"Will top up every existing course to {args.assignments_per_course} assignments. Run again with --apply after stopping the server.")
            return
        storage.initialize()
        print(json.dumps(top_up_assignments(args.assignments_per_course), ensure_ascii=False, indent=2))
        return
    if not args.apply:
        print("Will add 20 DEMO accounts, 3 courses, materials, assignments, submissions, attendance and notifications. Existing accounts/files are preserved. Run with --apply after stopping the server.")
        return
    storage.initialize()
    print(json.dumps(seed_demo(), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    from .runtime import data_lease
    from .config import DATA_DIR
    with data_lease(DATA_DIR):
        main()
