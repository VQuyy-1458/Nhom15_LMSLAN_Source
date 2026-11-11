"""Reusable papers, public course practice and fixed per-student code variants."""
import copy
import json
import secrets
import random
from datetime import datetime, timedelta, timezone
from . import learning, permissions, classification, exam_catalog
from .storage import read_json, write_json, utc_now, atomic_transaction, audit

PURPOSES = {'practice': 'Luyện tập', 'practical': 'Thực hành', 'exam': 'Thi'}
FORMATS = {'code': 'Code', 'file': 'Nộp file'}


def question_metadata(form, old=None):
    old = old or {}
    purpose = form.get('purpose', old.get('purpose', 'exam'))
    kind = form.get('submission_format', old.get('submission_format', 'code'))
    if purpose not in PURPOSES or kind not in FORMATS:
        raise learning.LearningError(400, 'Mục đích hoặc hình thức câu hỏi không hợp lệ.')
    return {'purpose': purpose, 'submission_format': kind}


def selected_questions(session, ids, kind='code'):
    if not ids or len(ids) > 30:
        raise learning.LearningError(400, 'Chọn từ 1 đến 30 câu hỏi.')
    bank = {q['id']: q for q in read_json('questions.json', [])}
    result = []
    for qid in ids:
        q = bank.get(qid)
        if q is None: raise learning.LearningError(404, 'Không tìm thấy câu hỏi.')
        permissions.require_content(session, q)
        if q.get('archived') or q.get('submission_format', 'code') != kind:
            raise learning.LearningError(400, 'Câu hỏi đã lưu trữ hoặc không đúng hình thức.')
        result.append(q)
    return result


def add_questions(session, form):
    ids = classification.values(form, 'question_ids', [])
    if not ids: return form
    questions = selected_questions(session, ids)
    try: problems = json.loads(form.get('problems', '[]'))
    except (ValueError, TypeError): raise learning.LearningError(400, 'Danh sách bài toán không hợp lệ.')
    if not isinstance(problems, list): raise learning.LearningError(400, 'Danh sách bài toán không hợp lệ.')
    languages = set(form.get('languages', '').split(','))
    for q in questions:
        if not languages.issubset(q['programming']['languages']):
            raise learning.LearningError(400, 'Các câu hỏi không hỗ trợ cùng ngôn ngữ.')
        problems.extend({**p, 'source_question_id': q['id']} for p in q['programming']['problems'])
    return {**form, 'problems': json.dumps(problems)}


def papers(session):
    if not permissions.staff(session): permissions.deny()
    return [p for p in read_json('exam_papers.json', []) if not p.get('archived') and permissions.manages(session, p)]


def manage_paper(session, action, form, ip):
    if not permissions.staff(session): permissions.deny()
    with learning.LOCK, atomic_transaction():
        rows = read_json('exam_papers.json', [])
        old = next((p for p in rows if p['id'] == form.get('id')), None)
        if form.get('id') and not old: raise learning.LearningError(404, 'Không tìm thấy đề thi.')
        if old: permissions.require_content(session, old)
        if action == 'save':
            cid = form.get('course_id')
            permissions.require_course(session, cid)
            learning.course_access(learning.load(), cid, session, write=True)
            kind = form.get('submission_format', 'code')
            if kind not in FORMATS: raise learning.LearningError(400, 'Hình thức đề không hợp lệ.')
            questions = selected_questions(session, classification.values(form, 'question_ids', []), kind)
            row = {'id': old['id'] if old else 'paper_'+secrets.token_hex(12), 'course_id': cid,
                   'created_by': old['created_by'] if old else session['user_id'], 'created_at': old['created_at'] if old else utc_now(),
                   'updated_at': utc_now(), 'title': learning.text(form, 'title'), 'submission_format': kind,
                   'question_ids': [q['id'] for q in questions], 'questions': copy.deepcopy(questions)}
            if kind == 'code':
                languages = set(questions[0]['programming']['languages'])
                for q in questions: languages.intersection_update(q['programming']['languages'])
                row['programming'] = exam_catalog.validate_programming({'languages': ','.join(sorted(languages)),
                    'problems': json.dumps([{**p, 'source_question_id': q['id']} for q in questions for p in q['programming']['problems']])})
                for p, q in zip(row['programming']['problems'], questions): p['source_question_id'] = q['id']
            rows = [p for p in rows if p['id'] != row['id']] + [row]
        elif action == 'archive':
            if not old: raise learning.LearningError(404, 'Không tìm thấy đề thi.')
            old['archived'] = True; row = old
        else: raise learning.LearningError(400, 'Thao tác không hợp lệ.')
        write_json('exam_papers.json', rows)
        audit('paper.'+action, session['user_id'], ip, {'id': row['id']})
        return {'ok': True, 'id': row['id']}


def apply_paper(session, form):
    if not form.get('paper_id'): return form
    paper = next((p for p in papers(session) if p['id'] == form['paper_id']), None)
    if not paper: raise learning.LearningError(404, 'Không tìm thấy đề thi thuộc quyền quản lý.')
    permissions.require_course(session, form.get('course_id'))
    if paper['submission_format'] != 'code': raise learning.LearningError(400, 'Chọn đề lập trình cho kỳ thi code.')
    return {**form, 'languages': ','.join(paper['programming']['languages']),
            'problems': json.dumps(paper['programming']['problems']), 'question_ids': '[]'}


def indices(row, sid):
    if row.get('variant_assignments') is not None:
        return row['variant_assignments'].get(sid, [])
    return list(range(len(row['programming']['problems'])))


def assign_variants(row, participants):
    mode = row.get('question_distribution', 'same')
    if mode == 'same': return
    count = row.get('questions_per_student', len(row['programming']['problems']))
    pool = list(range(len(row['programming']['problems'])))
    # Fixed snapshots survive reload/restart and never change a student's allocated set.
    assigned = row.setdefault('variant_assignments', {})
    generator = random.SystemRandom()
    for sid in participants:
        if sid not in assigned:
            assigned[sid] = generator.sample(pool, count)


def practice_catalog(session):
    if session.get('role') != 'student': permissions.deny()
    return [{k: q.get(k) for k in ('id','title','course_id','topic_ids','difficulty','submission_format','purpose')}
            for q in read_json('questions.json', []) if q.get('purpose') == 'practice' and q.get('published') and not q.get('archived')
            and permissions.course_allowed(session, q['course_id'])]


def start_practice(session, form, ip):
    if session.get('role') != 'student': permissions.deny()
    with learning.LOCK, atomic_transaction():
        if form.get('id') not in {q['id'] for q in practice_catalog(session)}: permissions.deny('Bài luyện tập chưa công bố hoặc không thuộc khóa học của bạn.')
        q = next(q for q in read_json('questions.json', []) if q['id'] == form['id'])
        learning.course_access(learning.load(), q['course_id'], session, write=True)
        sid = session['user_id']
        key = 'practice_'+__import__('hashlib').sha256((q['id']+':'+sid).encode()).hexdigest()[:28]
        due = (datetime.now(timezone.utc)+timedelta(days=3650)).isoformat()
        if q.get('submission_format', 'code') == 'code':
            rows = read_json('programming_assignments.json', [])
            if not any(r['id'] == key for r in rows):
                rows.append({'id': key, 'title': q['title'], 'description': 'Luyện tập tự chọn, không tính vào điểm khóa học.',
                             'course_id': q['course_id'], 'created_by': q['created_by'], 'created_at': utc_now(),
                             'type': 'programming', 'activity_type': 'assignment', 'assessment_type': 'practice', 'purpose': 'practice',
                             'programming': copy.deepcopy(q['programming']), 'topic_ids': q.get('topic_ids', []),
                             'difficulty': q.get('difficulty','medium'), 'state': 'started', 'participants': [sid],
                             'started_at': utc_now(), 'ends_at': due, 'due_at': due, 'duration_minutes': 0, 'source_question_id': q['id']})
                write_json('programming_assignments.json', rows)
            url = '/student/assignments?course='+q['course_id']+'&code_assignment='+key
        else:
            data = learning.load()
            if not any(r['id'] == key for r in data['assignments']):
                data['assignments'].append({'id': key, 'title': q['title'], 'description': q.get('statement',''), 'course_id': q['course_id'],
                    'created_by': q['created_by'], 'created_at': utc_now(), 'due_at': due, 'published': True,
                    'practice_owner': sid, 'purpose': 'practice', 'max_attempts': 20, 'source_question_id': q['id']})
                write_json('learning.json', data)
            url = '/student/assignments?course='+q['course_id']+'&assignment='+key
        audit('practice.start', sid, ip, {'question_id': q['id'], 'assignment_id': key})
        return {'ok': True, 'id': key, 'url': url}
