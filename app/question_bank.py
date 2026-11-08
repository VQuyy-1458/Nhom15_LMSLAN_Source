"""Reusable, course-scoped questions and paper definitions."""
from __future__ import annotations

import copy
import json
import random
import secrets

from . import learning, code_runner
from .config import EXAM_DIR
from .storage import read_json, write_json, audit, atomic_transaction, utc_now, save_payload


def questions():
    return read_json("question_bank.json", [])


def papers():
    return read_json("exam_papers.json", [])


def normalize_problem(problem):
    if not isinstance(problem, dict):
        raise learning.LearningError(400, "Bài toán không hợp lệ.")
    title = learning.text(problem, "title")
    statement = learning.text(problem, "statement", limit=20000, required=False)
    mode = problem.get("execution_mode", "stdin")
    if mode not in {"stdin", "harness"}:
        raise learning.LearningError(400, "Kiểu chạy bài toán không hợp lệ.")
    checker = problem.get("checker", "tokens")
    if checker not in {"tokens", "exact"}:
        raise learning.LearningError(400, "Cách so khớp kết quả không hợp lệ.")
    tests = problem.get("tests", [])
    if not isinstance(tests, list) or len(tests) > 100:
        raise learning.LearningError(400, "Mỗi bài toán có tối đa 100 test case.")
    cases = []
    for test in tests:
        if not isinstance(test, dict) or any(not isinstance(test.get(key, ""), str) or len(test.get(key, "")) > limit for key, limit in (("input", 100000), ("output", 100000), ("test_code", 20000))):
            raise learning.LearningError(400, "Dữ liệu test case không hợp lệ hoặc quá lớn.")
        if mode == "harness" and not test.get("test_code", "").strip():
            raise learning.LearningError(400, "Test class/method cần mã kiểm thử.")
        cases.append({"input": test.get("input", ""), "output": test.get("output", ""), "test_code": test.get("test_code", "") if mode == "harness" else "", "sample": test.get("sample") is True})
    result = {"title": title, "statement": statement, "points": learning.integer(problem, "points", 100, 1, 1000), "time_limit_ms": learning.integer(problem, "time_limit_ms", 1000, 100, 30000), "memory_limit_mb": learning.integer(problem, "memory_limit_mb", 256, 16, 2048), "checker": checker, "execution_mode": mode, "tests": cases}
    if not code_runner.budget_valid(result):
        raise learning.LearningError(400, "Số test và thời gian mỗi test vượt ngân sách chấm.")
    return result


def save_question(session, form, ip):
    with learning.LOCK, atomic_transaction():
        rows = questions()
        old = next((row for row in rows if row["id"] == form.get("id")), None)
        if form.get("id") and old is None:
            raise learning.LearningError(404, "Không tìm thấy câu hỏi.")
        course_id = learning.text(form, "course_id", 80)
        learning.course_access(learning.load(), course_id, session, write=True)
        if old and old["course_id"] != course_id:
            raise learning.LearningError(409, "Không thể chuyển câu hỏi sang khóa học khác.")
        kind = form.get("kind", "code")
        category = form.get("category", "practice")
        if kind not in {"code", "file"} or category not in {"practice", "lab", "exam"}:
            raise learning.LearningError(400, "Phân loại câu hỏi không hợp lệ.")
        if old and old["kind"] != kind and any(old["id"] in paper["question_ids"] for paper in papers()):
            raise learning.LearningError(409, "Câu hỏi đã nằm trong đề thi, không thể đổi hình thức nộp.")
        raw = form.get("problem", "{}")
        try:
            problem = json.loads(raw) if isinstance(raw, str) else raw
        except (TypeError, ValueError):
            raise learning.LearningError(400, "Nội dung câu hỏi không hợp lệ.")
        if kind == "code":
            problem = normalize_problem(problem)
        else:
            if not isinstance(problem, dict):
                raise learning.LearningError(400, "Nội dung câu hỏi không hợp lệ.")
            problem = {"title": learning.text(problem, "title"), "statement": learning.text(problem, "statement", limit=20000, required=False)}
        published = form.get("published", "false") == "true" and category == "practice"
        row = {"id": old["id"] if old else secrets.token_hex(10), "course_id": course_id, "kind": kind, "category": category, "published": published, "problem": problem, "created_at": old["created_at"] if old else utc_now(), "updated_at": utc_now()}
        rows = [entry for entry in rows if entry["id"] != row["id"]] + [row]
        write_json("question_bank.json", rows)
        audit("questions.saved", session["user_id"], ip, {"id": row["id"], "course_id": course_id})
        return {"ok": True, "question": row}


def save_paper(session, form, ip):
    with learning.LOCK, atomic_transaction():
        rows = papers()
        old = next((row for row in rows if row["id"] == form.get("id")), None)
        if form.get("id") and old is None:
            raise learning.LearningError(404, "Không tìm thấy đề thi.")
        course_id = learning.text(form, "course_id", 80)
        learning.course_access(learning.load(), course_id, session, write=True)
        kind = form.get("kind", "code")
        if kind not in {"code", "file"}:
            raise learning.LearningError(400, "Hình thức đề không hợp lệ.")
        ids = list(dict.fromkeys(form.get("question_ids", "").replace(",", " ").split()))
        bank = {q["id"]: q for q in questions()}
        if not ids or len(ids) > 30 or any(qid not in bank or bank[qid]["course_id"] != course_id or bank[qid]["kind"] != kind or bank[qid]["category"] != "exam" for qid in ids):
            raise learning.LearningError(400, "Chọn từ 1 đến 30 câu loại thi cùng khóa học và hình thức.")
        count = learning.integer(form, "question_count", len(ids), 1, len(ids))
        row = {"id": old["id"] if old else secrets.token_hex(10), "course_id": course_id, "kind": kind, "title": learning.text(form, "title"), "question_ids": ids, "question_count": count, "created_at": old["created_at"] if old else utc_now(), "updated_at": utc_now()}
        if kind == "file":
            # Keep every generated variant immutable: an ongoing release may
            # still reference files from an earlier paper revision.
            rng = random.Random(secrets.token_hex(16))
            selections = set()
            for _ in range(200):
                selections.add(tuple(sorted(rng.sample(ids, count))))
                if len(selections) >= 12:
                    break
            if not selections:
                selections.add(tuple(ids))
            files = []
            for index, selection in enumerate(sorted(selections), 1):
                filename = f"paper-{row['id']}-{secrets.token_hex(4)}-{index:02}.txt"
                contents = row["title"] + "\n\n" + "\n\n".join(f"Câu {number}. {bank[qid]['problem']['title']}\n{bank[qid]['problem']['statement']}" for number, qid in enumerate(selection, 1)) + "\n"
                save_payload(EXAM_DIR / filename, contents.encode("utf-8"))
                files.append(filename)
            row["generated_files"] = files
        write_json("exam_papers.json", [entry for entry in rows if entry["id"] != row["id"]] + [row])
        audit("papers.saved", session["user_id"], ip, {"id": row["id"], "course_id": course_id})
        return {"ok": True, "paper": row}


def public_practice(course_ids):
    return [{**{k: row[k] for k in ("id", "course_id", "kind", "category", "published")}, "problem": {**{k: row["problem"].get(k) for k in ("title", "statement", "points", "execution_mode")}, "samples": [case for case in row["problem"].get("tests", []) if case["sample"]]}} for row in questions() if row["course_id"] in course_ids and row["category"] == "practice" and row["published"]]
