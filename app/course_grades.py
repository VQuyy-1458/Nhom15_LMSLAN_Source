"""Course assessment marks normalized to a common ten-point scale."""
import math

from .storage import read_json


def valid_score(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def exam_marks(course_id, student_ids, *, exam_rows=None, file_submissions=None, code_submissions=None):
    from .exam_catalog import listing
    exams = [e for e in (exam_rows if exam_rows is not None else listing()) if e.get("course_id") == course_id and e.get("assessment_type") in {"practice", "midterm", "final"} and e.get("state") != "idle"]
    files = file_submissions if file_submissions is not None else read_json("submissions.json", {})
    code = code_submissions if code_submissions is not None else read_json("programming_submissions.json", [])
    indexed_code = {}
    for attempt in code:
        indexed_code.setdefault((attempt.get("exam_id"),attempt.get("student_id"),attempt.get("problem_index")),[]).append(attempt)
    result = {sid: [] for sid in student_ids}
    for exam in exams:
        for sid in student_ids:
            if sid not in exam.get("participants", []):
                continue
            score = None
            if exam["type"] == "file":
                attempts = [r for r in files.get(sid, []) if r.get("exam_id") == exam["id"] or (not r.get("exam_id") and exam.get("release_id") and r.get("release_id") == exam["release_id"])]
                # Legacy timestamps only have second precision; the later
                # appended receipt wins when two attempts share that timestamp.
                latest = max(reversed(attempts), key=lambda r: r.get("submitted_at", ""), default=None)
                if latest:
                    score = latest.get("score")
                elif exam["state"] == "ended":
                    score = 0
            else:
                problems = exam.get("programming", {}).get("problems", [])
                marks = []
                from .programming import assigned_indices
                assigned=assigned_indices(exam,sid)
                for index in assigned:
                    problem=problems[index]
                    attempts = indexed_code.get((exam["id"],sid,index),[])
                    points = []
                    for attempt in attempts:
                        grades = [h.get("result") for h in attempt.get("grading_history", [])] + [attempt.get("result")]
                        value = next((g["score"] for g in reversed(grades) if g and valid_score(g.get("score"))), None)
                        if value is not None:
                            points.append(max(0, min(problem["points"], value)))
                    marks.append(max(points) if points else 0 if not attempts and exam["state"] == "ended" else None)
                maximum = sum(problems[i]["points"] for i in assigned)
                if marks and maximum and all(v is not None for v in marks):
                    score = 10 * sum(marks) / maximum
            result[sid].append({"exam_id": exam["id"], "title": exam["title"], "assessment_type": exam["assessment_type"], "score": round(max(0, min(10, score)), 2) if valid_score(score) else None})
    return result
