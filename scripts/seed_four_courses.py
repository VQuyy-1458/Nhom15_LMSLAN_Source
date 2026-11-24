"""Build an isolated, replaceable four-course LAN-LMS trial dataset."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def oop_examples():
    point = {
        "title": "Java OOP · Lớp Point và các phép di chuyển",
        "statement": "Viết public class Point với hai thuộc tính private double positionX, positionY; constructor mặc định và constructor nhận x, y; getter, setter, moveRight, moveUp và toString theo mẫu Point(x,y). Nộp mã lớp Point, không viết main.",
        "points": 10, "time_limit_ms": 2000, "memory_limit_mb": 256,
        "checker": "tokens", "language": "java", "answer_kind": "class",
        "starter_code": "public class Point {\n    private double positionX;\n    private double positionY;\n    // Hoàn thiện constructor và phương thức\n}\n",
        "oop_rubric": {"version": 1, "class_name": "Point", "criteria": [
            {"kind": "class", "access": "public", "points": 1},
            {"kind": "field", "name": "positionX", "type": "double", "access": "private", "points": 1},
            {"kind": "field", "name": "positionY", "type": "double", "access": "private", "points": 1},
            {"kind": "constructor", "parameters": [], "access": "public", "points": 1},
            {"kind": "constructor", "parameters": ["double", "double"], "access": "public", "points": 1},
            {"kind": "method", "name": "getPositionX", "parameters": [], "return_type": "double", "access": "public", "points": .5},
            {"kind": "method", "name": "getPositionY", "parameters": [], "return_type": "double", "access": "public", "points": .5},
            {"kind": "method", "name": "moveRight", "parameters": ["double"], "return_type": "void", "access": "public", "points": 1},
            {"kind": "method", "name": "moveUp", "parameters": ["double"], "return_type": "void", "access": "public", "points": 1},
        ]},
        "tests": [
            {"input": "", "output": "Point(3.0,4.0)", "sample": True, "points": 2,
             "test_code": "Point p = new Point(1, 2); p.moveRight(2); p.moveUp(2); System.out.print(p);", "criterion": "Di chuyển và hiển thị"},
        ],
    }
    counter = {
        "title": "Java OOP · Counter: cấu trúc và hành vi",
        "statement": "Viết public class Counter có private int value, constructor nhận giá trị đầu, hàm public int add(int n) trả về value+n. Hệ thống kiểm tra riêng class, field, constructor, method và kết quả chạy.",
        "points": 10, "time_limit_ms": 2000, "memory_limit_mb": 256,
        "checker": "tokens", "language": "java", "answer_kind": "class",
        "starter_code": "public class Counter {\n    private int value;\n    public Counter(int value) { this.value = value; }\n    public int add(int n) { return value + n; }\n}\n",
        "oop_rubric": {"version": 1, "class_name": "Counter", "criteria": [
            {"kind": "class", "access": "public", "points": 1},
            {"kind": "field", "name": "value", "type": "int", "access": "private", "points": 2},
            {"kind": "constructor", "parameters": ["int"], "access": "public", "points": 1},
            {"kind": "method", "name": "add", "parameters": ["int"], "return_type": "int", "access": "public", "points": 2},
        ]},
        "tests": [{"input": "", "output": "5", "sample": True, "points": 4,
                   "test_code": "System.out.print(new Counter(3).add(2));", "criterion": "Cộng giá trị"}],
    }
    student = {
        "title": "Java OOP · Quản lý sinh viên và sắp xếp GPA",
        "statement": "Viết chương trình Java có lớp SinhVien với các thuộc tính private maSV, hoTen, lop, ns, gpa; constructor, getter, chuẩn hóa họ tên và ngày sinh, toString. Lớp Main đọc n sinh viên, sắp xếp GPA giảm dần và in kết quả. Nộp chương trình đầy đủ có main. Hệ thống kiểm tra cả cấu trúc lớp và output.",
        "points": 10, "time_limit_ms": 2000, "memory_limit_mb": 256,
        "checker": "tokens", "language": "java", "answer_kind": "program",
        "oop_rubric": {"version": 1, "class_name": "SinhVien", "criteria": [
            {"kind": "class", "access": "package", "points": .5},
            {"kind": "field", "name": "maSV", "type": "java.lang.String", "access": "private", "points": .5},
            {"kind": "field", "name": "hoTen", "type": "java.lang.String", "access": "private", "points": .5},
            {"kind": "field", "name": "lop", "type": "java.lang.String", "access": "private", "points": .5},
            {"kind": "field", "name": "ns", "type": "java.lang.String", "access": "private", "points": .5},
            {"kind": "field", "name": "gpa", "type": "double", "access": "private", "points": .5},
            {"kind": "constructor", "parameters": ["java.lang.String", "java.lang.String", "java.lang.String", "double"], "access": "public", "points": 1},
            {"kind": "method", "name": "getGpa", "parameters": [], "return_type": "double", "access": "public", "points": 1},
        ]},
        "tests": [
            {"input": "1\n  nGuYEn   vaN   aN  \nD22CQCN01-B\n1/2/2004\n8.5\n", "output": "B20DCCN001 Nguyen Van An D22CQCN01-B 01/02/2004 8.50\n", "sample": True, "points": 2.5, "criterion": "Một sinh viên"},
            {"input": "2\ntran thi binh\nD22\n12/10/2003\n7.0\nle minh chau\nD22\n2/3/2004\n9.0\n", "output": "B20DCCN002 Le Minh Chau D22 02/03/2004 9.00\nB20DCCN001 Tran Thi Binh D22 12/10/2003 7.00\n", "sample": False, "points": 2.5, "criterion": "Sắp xếp theo GPA"},
        ],
    }
    return [point, counter, student]


def main():
    from app import config, storage, learning, exercise_bank, question_papers, exam_catalog, course_content, course_schedule, programming_assignments, code_runner
    from app.security import hash_password
    from app.seed_demo import NAMES

    stage = config.RUNTIME_DIR
    if not stage.is_relative_to(ROOT / "backups") or not stage.name.startswith(".staging-trial-"):
        raise RuntimeError("CSS_DATA_ROOT phải trỏ tới thư mục staging của project.")
    for name in ("data", "learning-files", "submissions", "de-thi", "programming-submissions", "demo-inputs"):
        (stage / name).mkdir(parents=True, exist_ok=True)
    storage.initialize()
    admin = {"role": "admin", "user_id": "admin"}
    ip = "127.0.0.1"
    now = datetime.now(timezone.utc)
    stamp = lambda value: value.isoformat()
    names = NAMES + ["Nguyễn Đức Anh", "Trần Gia Bảo", "Lê Thanh Bình", "Phạm Minh Đức", "Hoàng Thu Hà", "Võ Minh Hiếu", "Đặng Khánh Hòa", "Bùi Nhật Huy", "Đỗ Mai Lan", "Ngô Minh Long", "Nguyễn Tuấn Minh", "Trần Thảo My", "Lê Phương Nam", "Phạm Ngọc Nhi", "Hoàng Văn Phúc", "Võ Anh Quân", "Đặng Minh Tâm", "Bùi Đức Thắng", "Đỗ Thùy Trang", "Ngô Tuấn Tú"]
    students = {f"SV{i:03}": {"student_id": f"SV{i:03}", "full_name": names[i-1], "password_hash": hash_password("111111"), "active": True, "created_at": stamp(now), "must_change_password": False, "last_ip": None, "last_seen": None} for i in range(1,41)}
    storage.write_json("students.json", students)
    course_specs = [
        ("cpp", "CPP-01", "Lập trình C++", 2, ["Nhập xuất và kiểu dữ liệu", "Rẽ nhánh, vòng lặp", "Mảng và vector", "Hàm và đệ quy", "Chuỗi và sắp xếp", "Tìm kiếm, thuật toán", "Ôn tập và thực hành tổng hợp"]),
        ("java", "JAVA-OOP-01", "Lập trình Java OOP", 3, ["Java cơ bản và kiểu dữ liệu", "Class và object", "Attribute và constructor", "Đóng gói, getter/setter", "Kế thừa và đa hình", "Collection và sắp xếp", "Bài OOP hoàn chỉnh"]),
        ("python", "PY-01", "Lập trình Python", 4, ["Cú pháp và nhập xuất", "Điều kiện, vòng lặp", "List và tuple", "Hàm, module", "Dictionary và string", "File và ngoại lệ", "Thuật toán và tổng hợp"]),
        ("network", "LTM-01", "Lập trình mạng", 5, ["Mô hình TCP/IP", "Địa chỉ IPv4 và subnet", "Socket TCP", "Socket UDP", "Giao thức ứng dụng", "Truyền file và đa luồng", "Client–Server tổng hợp"]),
    ]
    roster = " ".join(students)
    course_ids = {}
    for key, code, title, _, _ in course_specs:
        course_ids[key] = learning.mutate(admin, "course", {"name": title, "code": code, "group": "Nhóm 01", "semester": "Học kỳ 1 · 2026–2027", "description": f"Khóa học 7 tuần {title}; học liệu, bài tập, thực hành và kỳ thi cùng một không gian.", "student_ids": roster, "enrollment": "selected"}, {}, ip)["id"]
    source = json.loads((ROOT / "resources" / "code_catalogue" / "questions.json").read_text(encoding="utf-8"))
    bank_ids = {key: [] for key in course_ids}
    for key, _, _, _, _ in course_specs[:3]:
        group = [row for row in source if row["language"] == key]
        for index, entry in enumerate(group):
            purpose = "practice" if entry["practice"] else "practical" if index < 14 else "exam"
            week = index % 7 + 1
            form = {"title": entry["title"], "statement": entry["statement"], "course_ids": json.dumps([course_ids[key]]), "purpose": purpose, "response_type": "code", "languages": key, "problems": json.dumps(entry["programming"]["problems"]), "source_url": entry.get("source_url", ""), "week_number": str(week)}
            qid = exercise_bank.manage_question(admin, "save", form, ip)["id"]
            if purpose == "practice": exercise_bank.manage_question(admin, "publish", {"id": qid}, ip)
            bank_ids[key].append((qid, purpose, week))
    network_tasks = [
        ("Kiểm tra octet IPv4", "Đọc bốn số nguyên, in VALID nếu mọi số từ 0 đến 255, ngược lại INVALID.", [("192 168 1 1\n", "VALID\n"), ("256 1 1 1\n", "INVALID\n")]),
        ("Chuyển IPv4 sang số 32 bit", "Đọc bốn octet IPv4, in giá trị nguyên không dấu tương ứng.", [("0 0 0 1\n", "1\n"), ("192 168 1 1\n", "3232235777\n")]),
        ("Tính số địa chỉ trong subnet", "Đọc prefix p từ 0 đến 32, in 2^(32-p).", [("24\n", "256\n"), ("32\n", "1\n")]),
        ("Kiểm tra cổng dịch vụ", "Đọc số cổng, in VALID nếu 1..65535, ngược lại INVALID.", [("8080\n", "VALID\n"), ("70000\n", "INVALID\n")]),
        ("Đếm byte của thông điệp UTF-8", "Đọc một dòng ASCII không dấu, in số ký tự của dòng.", [("HELLO LAN\n", "9\n"), ("TCP\n", "3\n")]),
        ("Phân loại TCP và UDP", "Đọc TCP hoặc UDP; in RELIABLE cho TCP và DATAGRAM cho UDP.", [("TCP\n", "RELIABLE\n"), ("UDP\n", "DATAGRAM\n")]),
        ("Tính độ dài gói dữ liệu", "Đọc header và payload (byte), in tổng số byte của gói.", [("20 512\n", "532\n"), ("8 0\n", "8\n")]),
    ]
    for index, (title, statement, cases) in enumerate(network_tasks):
        problem = {"title": title, "statement": statement, "points": 100, "time_limit_ms": 1000, "memory_limit_mb": 256, "checker": "tokens", "tests": [{"input": a, "output": b, "sample": i == 0} for i, (a, b) in enumerate(cases)]}
        qid = exercise_bank.manage_question(admin, "save", {"title": title, "statement": statement, "course_ids": json.dumps([course_ids["network"]]), "purpose": "practice", "response_type": "code", "languages": "cpp,java,python", "problems": json.dumps([problem]), "week_number": str(index+1)}, ip)["id"]
        exercise_bank.manage_question(admin, "publish", {"id": qid}, ip)
        bank_ids["network"].append((qid, "practice", index+1))
    oop_ids = []
    for week, problem in zip((2, 4, 7), oop_examples()):
        config = exam_catalog.validate_programming({"languages": "java", "problems": json.dumps([problem])})
        qid = exercise_bank.manage_question(admin, "save", {"title": problem["title"], "statement": problem["statement"], "course_ids": json.dumps([course_ids["java"]]), "purpose": "practice" if week != 7 else "practical", "response_type": "code", "languages": "java", "problems": json.dumps(config["problems"]), "week_number": str(week)}, ip)["id"]
        if week != 7: exercise_bank.manage_question(admin, "publish", {"id": qid}, ip)
        bank_ids["java"].append((qid, "practice" if week != 7 else "practical", week))
        oop_ids.append(qid)
    # Seven dated lessons and seven linked learning plans in every course.
    monday = (now + timedelta(hours=7)).date() - timedelta(days=(now + timedelta(hours=7)).weekday()) - timedelta(weeks=3)
    iso = lambda day: f"{day.isocalendar().year}-W{day.isocalendar().week:02}"
    week_start, week_end = iso(monday), iso(monday+timedelta(weeks=6))
    for key, _, title, weekday, topics in course_specs:
        cid = course_ids[key]
        schedule = course_schedule.bulk(admin, {"course_id": cid, "title": title + " · buổi học", "description": "Học nội dung theo tuần, xem bài đọc và thực hành trên LAN-LMS.", "start_week": week_start, "end_week": week_end, "weekday": str(weekday), "start_time": "07:30", "end_time": "10:00", "location": "Phòng máy LAN"}, ip)
        assert schedule["created"] == 7
        lesson_rows = {row["week_number"]: row for row in learning.load()["events"] if row["course_id"] == cid and row["kind"] == "lesson"}
        for week, topic in enumerate(topics, 1):
            lesson = lesson_rows[week]
            material = learning.mutate(admin, "material", {"course_id": cid, "title": f"Tuần {week}: {topic}", "description": f"Mục tiêu, khái niệm và ví dụ của {topic}. Đọc trước khi làm bài tập code.", "week_number": str(week)}, {"file": {"filename": f"{key}-tuan-{week}.txt", "data": (f"{title} — Tuần {week}: {topic}\nĐọc đề bài, làm bài luyện tập, kiểm thử mẫu và xem phản hồi.\n").encode("utf-8")}}, ip)["id"]
            notice = learning.mutate(admin, "event", {"course_id": cid, "title": f"Nội dung tuần {week}: {topic}", "description": f"Tài liệu và bài code tuần {week} đã có trong khóa học.", "kind": "announcement", "starts_at": lesson["starts_at"]}, {}, ip)["id"]
            assignment = learning.mutate(admin, "assignment", {"course_id": cid, "title": f"Báo cáo thực hành tuần {week}: {topic}", "description": "Nộp PDF/TXT/ZIP mô tả cách giải, test biên và kết quả thực hành.", "due_at": stamp(now+timedelta(days=14+week*7)), "max_attempts": "6", "week_number": str(week)}, {}, ip)["id"]
            questions = [qid for qid, purpose, qweek in bank_ids[key] if purpose == "practice" and qweek == week]
            if not questions:
                # Some sourced questions are private; publish one weekly exercise for students.
                qid = next(qid for qid, purpose, qweek in bank_ids[key] if qweek == week)
                exercise_bank.manage_question(admin, "publish", {"id": qid}, ip)
                questions = [qid]
            activities = [exercise_bank.practice_id(next(q for q in exercise_bank.bank() if q["id"] == qid), cid) for qid in questions]
            practical_id = exercise_bank.manage_session(admin, "save", {"course_id": cid, "title": f"Thực hành tuần {week}: {topic}", "description": "Bài lấy từ kho chung. Giảng viên mở phiên để sinh viên bắt đầu làm bài.", "response_type": "code", "question_ids": json.dumps(questions[:1]), "duration_minutes": "90", "week_number": str(week)}, ip)["id"]
            activities.append(practical_id)
            course_content.save(admin, {"course_id": cid, "week_number": str(week), "title": f"Tuần {week} · {topic}", "lesson_text": f"Buổi {week}: {topic}. Học lý thuyết, thử ví dụ và thực hành trên máy.", "reading_text": f"Đọc tài liệu tuần {week}, ghi chú các trường hợp biên trước khi nộp code.", "material_ids": json.dumps([material]), "assignment_ids": json.dumps([assignment]), "announcement_ids": json.dumps([notice]), "activity_ids": json.dumps(activities)}, ip)
            if week <= 3:
                data = learning.load()
                records = {sid: {"status": "late" if (i+week)%11 == 0 else "present", "checked_in_at": lesson["starts_at"], "reason": ""} for i, sid in enumerate(students) if (i+week)%9 != 0}
                data["attendance"].append({"id": "att-"+key+"-"+str(week), "course_id": cid, "event_id": lesson["id"], "lesson_at": lesson["starts_at"], "title": lesson["title"], "description": "Điểm danh theo lịch học", "expires_at": lesson["ends_at"], "closed": True, "mode": "lan", "grace_minutes": 5, "code": secrets.token_hex(4).upper(), "records": records, "created_at": lesson["starts_at"]})
                storage.write_json("learning.json", data)
    # Reusable papers and a small exam set per course. Java has a live OOP test.
    papers = {}
    exams = {}
    for key, _, title, _, _ in course_specs:
        cid = course_ids[key]
        private = [qid for qid, purpose, _ in bank_ids[key] if purpose != "practice"]
        pool = private[:4] if len(private) >= 4 else [qid for qid, _, _ in bank_ids[key]][:4]
        pid = question_papers.manage(admin, "save", {"title": title + " · đề dùng lại", "description": "Chọn câu từ kho để giao thực hành và thi.", "response_type": "code", "question_ids": json.dumps(pool)}, ip)["id"]
        question_papers.manage(admin, "publish", {"id": pid}, ip)
        papers[key] = pid
        for kind in ("test", "midterm", "final"):
            selected = oop_ids[1:2] if key == "java" and kind == "test" else pool[:1]
            exam_id = exam_catalog.save(admin, {"course_id": cid, "title": f"{title} · " + {"test": "Thi thử code", "midterm": "Giữa kỳ", "final": "Cuối kỳ"}[kind], "description": "Đề được lấy từ kho câu hỏi; tự chấm bằng bộ chấm Docker.", "type": "programming", "assessment_type": kind, "languages": "java" if key == "java" else "cpp" if key == "cpp" else "python" if key == "python" else "cpp,java,python", "problems": json.dumps([next(q for q in exercise_bank.bank() if q["id"] == qid)["programming"]["problems"][0] for qid in selected]), "duration_minutes": "180", "participant_ids": "\n".join(students)}, ip)["id"]
            exams[key+"-"+kind] = exam_id
    if not code_runner.ready():
        raise RuntimeError("Docker judge chưa sẵn sàng; chưa thay dữ liệu đang chạy.")
    oop_practical = exercise_bank.manage_session(admin, "save", {"course_id": course_ids["java"], "title": "Thực hành Java OOP · bài hoàn chỉnh có main", "description": "Mở bài Quản lý sinh viên từ kho, nộp chương trình đầy đủ và xem điểm cấu trúc/hành vi.", "response_type": "code", "question_ids": json.dumps([oop_ids[2]]), "duration_minutes": "240", "week_number": "7"}, ip)["id"]
    exercise_bank.manage_session(admin, "start", {"id": oop_practical}, ip)
    for key in ("cpp", "java", "python", "network"):
        from app import programming
        programming.control(admin, {"exam_id": exams[key+"-test"], "action": "start"}, ip)
    # Two real judge outcomes demonstrate structure vs behavior in the admin archive.
    counter = next(q for q in exercise_bank.bank() if q["id"] == oop_ids[1])["programming"]["problems"][0]
    demo_sources = [
        ("SV002", "public class Counter { private int value; public Counter(int n){value=n;} public int add(int n){return value+n;} }", "AC"),
        ("SV003", "public class Counter { public int value; public Counter(int n){value=n;} public int add(int n){return value+n;} }", "WA"),
    ]
    rows = []
    for sid, source_code, verdict in demo_sources:
        result = code_runner.judge(source_code.encode(), "java", counter)
        if result["verdict"] != verdict: raise RuntimeError(f"Judge mismatch {sid}: {result['verdict']} != {verdict}")
        rid = "seed-oop-"+sid
        folder = stage / "programming-submissions" / rid
        folder.mkdir()
        (folder / "source").write_text(source_code, encoding="utf-8")
        write(folder / "problem.json", counter)
        rows.append({"id": rid, "exam_id": exams["java-test"], "exam_title": "Lập trình Java OOP · Thi thử code", "course_id": course_ids["java"], "student_id": sid, "full_name": students[sid]["full_name"], "problem_index": 0, "problem_title": counter["title"], "max_score": 10, "language": "java", "original_filename": "Counter.java", "submitted_at": stamp(now), "state": "done", "result": result, "size_bytes": len(source_code.encode()), "sha256": hashlib.sha256(source_code.encode()).hexdigest(), "ip": ip, "grading_history": [{"id": rid+"-grade", "result": result, "graded_at": stamp(now), "graded_by": "judge"}], "graded_at": stamp(now)})
    storage.write_json("programming_submissions.json", rows)
    data = learning.load()
    for course in data["courses"]:
        course["weights"] = {"attendance": 10, "homework": 20, "midterm": 30, "final": 40}
        tasks = [a for a in data["assignments"] if a["course_id"] == course["id"]][:2]
        for task in tasks:
            for i, sid in enumerate(list(students)[1:11]):
                rid = "report-" + task["id"] + "-" + sid
                content = ("Báo cáo: " + task["title"] + "\nSinh viên: " + students[sid]["full_name"] + "\nPhân tích yêu cầu, xây dựng lời giải và thử các tình huống biên.\n").encode("utf-8")
                filename = rid + ".txt"
                (stage / "learning-files" / filename).write_bytes(content)
                score = round(6 + i * .3, 2) if i < 7 else None
                row = {"id": rid, "course_id": course["id"], "assignment_id": task["id"], "assignment_title": task["title"], "course_name": course["name"], "student_id": sid, "full_name": students[sid]["full_name"], "created_at": stamp(now), "attempt": 1, "request_id": rid, "original_filename": sid + "_bao_cao.txt", "stored_name": filename, "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(), "ip": ip, "score": score, "feedback": "Đáp ứng yêu cầu; cần bổ sung kiểm thử biên." if score is not None else "", "grading_history": []}
                if score is not None:
                    row.update(graded_at=stamp(now), graded_by="admin")
                    row["grading_history"] = [{"id": rid+"-grade", "score": score, "feedback": row["feedback"], "graded_at": stamp(now), "graded_by": "admin"}]
                data["submissions"].append(row)
    storage.write_json("learning.json", data)
    full_program = '''import java.util.*;
class SinhVien {
  private static int count=0;
  private String maSV, hoTen, lop, ns;
  private double gpa;
  public SinhVien(String name,String klass,String birth,double score) {
    maSV=String.format("B20DCCN%03d",++count);
    StringBuilder b=new StringBuilder();
    for(String word:name.trim().split("\\s+")) b.append(Character.toUpperCase(word.charAt(0))).append(word.substring(1).toLowerCase()).append(' ');
    hoTen=b.toString().trim(); lop=klass; String[] p=birth.trim().split("/");
    ns=String.format("%02d/%02d/%s",Integer.parseInt(p[0]),Integer.parseInt(p[1]),p[2]); gpa=score;
  }
  public double getGpa(){return gpa;}
  public String toString(){return String.format("%s %s %s %s %.2f",maSV,hoTen,lop,ns,gpa);}
}
public class Main {
  public static void main(String[] args){Scanner sc=new Scanner(System.in); int n=Integer.parseInt(sc.nextLine()); List<SinhVien> a=new ArrayList<>();
    for(int i=0;i<n;i++){String name=sc.nextLine(),klass=sc.nextLine(),birth=sc.nextLine();double score=Double.parseDouble(sc.nextLine());a.add(new SinhVien(name,klass,birth,score));}
    a.sort((x,y)->Double.compare(y.getGpa(),x.getGpa()));for(SinhVien s:a)System.out.println(s);
  }
}
'''
    full_problem = next(q for q in exercise_bank.bank() if q["id"] == oop_ids[2])["programming"]["problems"][0]
    full_result = code_runner.judge(full_program.encode(), "java", full_problem)
    if full_result["verdict"] != "AC": raise RuntimeError("Full OOP program judge failed: " + json.dumps(full_result, ensure_ascii=False)[:4000])
    (stage / "demo-inputs" / "Main.java").write_text(full_program, encoding="utf-8")
    (stage / "demo-inputs" / "Counter.java").write_text(demo_sources[0][1], encoding="utf-8")
    (stage / "demo-inputs" / "Counter-sai-thuoc-tinh.java").write_text(demo_sources[1][1], encoding="utf-8")
    storage.write_json("notifications.json", [{"id": "notice-"+key, "student_id": None, "title": "Khóa học đã có nội dung 7 tuần", "message": f"{title}: xem lịch học, tài liệu và bài code theo từng tuần.", "created_at": stamp(now), "created_by": "Giảng viên"} for key, _, title, _, _ in course_specs])
    marker = {"version": "four-courses-7-weeks-v1", "created_at": stamp(now), "courses": course_ids, "students": list(students), "exams": exams, "oop_practical": oop_practical, "counts": {"courses": 4, "students": 40, "weeks": 28, "lessons": 28, "questions": len(exercise_bank.bank()), "oop_questions": len(oop_ids), "materials": len(learning.load()["materials"]), "assignments": len(learning.load()["assignments"]), "exams": len(exams), "judged_attempts": len(rows), "full_oop_program_verdict": full_result["verdict"]}}
    storage.write_json("demo_seed.json", marker)
    # Export canonical SQLite documents; apply() updates JSON immediately before first import.
    for name in storage.document_names():
        write(stage / "data" / name, storage.read_json(name))
    for suffix in ("", "-wal", "-shm"):
        (stage / "data" / ("lms.sqlite3"+suffix)).unlink(missing_ok=True)
    write(stage / "demo-inputs" / "HUONG_DAN.json", {"accounts": "SV001..SV040 / 111111", "admin_password": "Giữ nguyên mật khẩu hiện tại", "oop_examples": [p["title"] for p in oop_examples()], "course_ids": course_ids})
    from app.reset_demo import validate
    validate(stage)
    print(json.dumps({"staging": str(stage), **marker}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    stage = Path(args.stage).resolve()
    if not stage.is_relative_to(ROOT / "backups") or not stage.name.startswith(".staging-trial-"):
        parser.error("Stage must be inside project backups and start .staging-trial-")
    os.environ["CSS_DATA_ROOT"] = str(stage)
    main()
