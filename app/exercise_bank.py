"""Practice questions and timed practical sessions reuse the existing judge/archive."""
import copy
import json
import secrets
import threading
from datetime import datetime, timedelta, timezone
from . import learning, code_runner, exam_catalog
from .storage import read_json, write_json, atomic_transaction, utc_now, audit

BANK = 'course_questions.json'
SESSIONS = 'course_practicals.json'
PURPOSES = {'practice': 'Luyện tập', 'practical': 'Thực hành', 'exam': 'Thi'}
FUTURE = '2099-12-31T23:59:59+00:00'
_runs = threading.BoundedSemaphore(2)


def staff(session):
    if session['role'] != 'admin':
        raise learning.LearningError(403, 'Chỉ giảng viên được quản lý kho câu hỏi.')


def bank():
    return read_json(BANK, [])


def sessions():
    rows = read_json(SESSIONS, [])
    now = datetime.now(timezone.utc)
    for row in rows:
        if row['state'] == 'started' and learning.date_value(row['ends_at']) <= now:
            row['state'] = 'ended'
    return rows


def members(course, students=None):
    students = students if students is not None else read_json('students.json')
    return [sid for sid, s in students.items() if s.get('active', True) and (course.get('student_ids') is None or sid in course['student_ids'])]


def configuration(form):
    config = exam_catalog.validate_programming(form)
    if not config['problems'] or any(not p['tests'] for p in config['problems']):
        raise learning.LearningError(400, 'Cần ít nhất một bài toán với test case.')
    return config


def manage_question(session, action, form, ip):
    staff(session)
    with learning.LOCK, atomic_transaction():
        rows = bank()
        old = next((r for r in rows if r['id'] == form.get('id')), None)
        if (form.get('id') or action != 'save') and not old:
            raise learning.LearningError(404, 'Không tìm thấy câu hỏi.')
        from .course_content import ids
        course_ids=ids(form,'course_ids') if 'course_ids' in form else (old.get('course_ids',[old['course_id']] if old.get('course_id') else []) if old else ([form['course_id']] if form.get('course_id') else []))
        data=learning.load()
        if any(not any(c['id']==cid for c in data['courses']) for cid in course_ids):
            raise learning.LearningError(400,'Khóa học liên kết không tồn tại.')
        cid=old.get('course_id') if old else (course_ids[0] if course_ids else None)
        if action == 'save':
            purpose = form.get('purpose', 'practical')
            kind = form.get('response_type', 'code')
            if purpose not in PURPOSES or kind not in {'file', 'code'}:
                raise learning.LearningError(400, 'Chọn đúng mục đích và hình thức câu hỏi.')
            if old and old.get('published'):
                raise learning.LearningError(409, 'Ẩn bài luyện tập trước khi sửa đề; bài đã giao vẫn giữ bản chụp cũ.')
            row = {'id': old['id'] if old else 'q_' + secrets.token_hex(10), 'course_id': cid,
                   'course_ids':course_ids,'practice_key_version':old.get('practice_key_version',1) if old else 2,
                   'source_url':form.get('source_url',old.get('source_url','') if old else '').strip(),
                   'title': learning.text(form, 'title'), 'statement': learning.text(form, 'statement', 20000, False),
                   'purpose': purpose, 'response_type': kind, 'week_number': learning.integer(form, 'week_number', 0, 0, 52),
                   'published': False, 'archived': False, 'created_by': session['user_id'],
                   'created_at': old['created_at'] if old else utc_now(), 'updated_at': utc_now()}
            if row['source_url']:
                from urllib.parse import urlsplit
                source=urlsplit(row['source_url'])
                if source.scheme not in {'https','http'} or not source.hostname:raise learning.LearningError(400,'Nguồn bài phải là URL HTTP/HTTPS.')
            if kind == 'code':
                row['programming'] = configuration(form)
            else:
                extensions = sorted(set(form.get('extensions', '.pdf .txt .zip').replace(',', ' ').split()))
                if not extensions or not set(extensions).issubset(learning.FILE_SUBMISSION_EXTENSIONS):
                    raise learning.LearningError(400, 'Chọn định dạng tài liệu hoặc ZIP hợp lệ.')
                if not row['statement']:
                    raise learning.LearningError(400, 'Nhập yêu cầu bài nộp file.')
                row['extensions'] = extensions
            rows = [r for r in rows if r['id'] != row['id']] + [row]
        elif action in {'publish', 'unpublish', 'archive'}:
            row = old
            if action == 'publish' and row.get('archived'):
                raise learning.LearningError(409, 'Không công bố câu đã lưu trữ.')
            row['published'] = action == 'publish'
            if action == 'archive':
                row['archived'] = True
        else:
            raise learning.LearningError(400, 'Thao tác không hợp lệ.')
        write_json(BANK, rows)
        sync_file_practice(row)
        audit('learning.question_' + action, session['user_id'], ip, {'id': row['id']})
        return {'ok': True, 'id': row['id']}


def linked_courses(question, courses=None):
    ids=question.get('course_ids', [question['course_id']] if question.get('course_id') else [])
    courses = courses if courses is not None else learning.load()['courses']
    return [c for c in courses if c['status']!='completed' and (not ids or c['id'] in ids)]


def practice_id(question,cid):
    if question.get('practice_key_version',1)==1 and question.get('course_id')==cid:return 'practice_'+question['id']
    return 'practice_'+question['id']+'_'+cid


def sync_file_practice(question):
    data=learning.load();active=question['response_type']=='file' and question.get('published') and not question.get('archived')
    valid=set()
    if active:
        for course in linked_courses(question):
            item_id=practice_id(question,course['id']);valid.add(item_id)
            row={'id':item_id,'course_id':course['id'],'title':question['title'],'description':question['statement'],
                 'topic':'Luyện tập','week_number':question['week_number'],'practice':True,'due_at':FUTURE,
                 'max_attempts':20,'accepted_extensions':question['extensions'],'created_at':question['created_at'],
                 'source_question_id':question['id'],'published':True,'archived':False}
            old=next((a for a in data['assignments'] if a['id']==item_id),None)
            if old:old.update(row)
            else:data['assignments'].append(row)
    changed=bool(valid)
    for row in data['assignments']:
        if (row.get('source_question_id')==question['id'] or row['id']=='practice_'+question['id']) and row['id'] not in valid:
            row['archived']=True;changed=True
    if changed:write_json('learning.json',data)


def selection(form, purpose, course_id, response):
    from .question_papers import selected
    from .course_content import ids
    return selected(ids(form,'question_ids'),response)


def manage_session(session, action, form, ip):
    staff(session)
    with learning.LOCK, atomic_transaction():
        rows = sessions()
        old = next((r for r in rows if r['id'] == form.get('id')), None)
        if (form.get('id') or action != 'save') and not old:
            raise learning.LearningError(404, 'Không tìm thấy buổi thực hành.')
        cid = old['course_id'] if old else form.get('course_id')
        course = learning.course_access(learning.load(), cid, session, write=True)
        if action == 'save':
            if old and old['state'] != 'idle':
                raise learning.LearningError(409, 'Phiên đã mở, không được sửa đề.')
            kind = form.get('response_type', 'code')
            from . import question_papers
            resolved=question_papers.resolve(form,kind)
            questions=selection(form,'practical',cid,kind) if not resolved else []
            selected = list(dict.fromkeys(form.get('student_ids', '').replace(',', ' ').split())) or members(course)
            if not selected or not set(selected).issubset(members(course)):
                raise learning.LearningError(400, 'Danh sách sinh viên không hợp lệ.')
            row = {'id': old['id'] if old else 'practical_' + secrets.token_hex(10), 'course_id': cid,
                   'title': learning.text(form, 'title'), 'description': learning.text(form, 'description', 10000, False),
                   'response_type': kind, 'type': 'programming' if kind == 'code' else 'file',
                   'duration_minutes': learning.integer(form, 'duration_minutes', 60, 1, 480),
                   'week_number': learning.integer(form, 'week_number', 0, 0, 52), 'participants': selected,
                   'state': 'idle', 'activity_type': 'practical', 'assessment_type': 'practice',
                   'created_at': old['created_at'] if old else utc_now(), 'created_by': session['user_id'],
                   'question_ids': [q['id'] for q in questions]}
            if resolved:
                row.update(resolved)
                row['question_ids']=list(dict.fromkeys(q['id'] for p in resolved['paper_snapshots'] for q in p['questions']))
            elif kind=='code':row['programming']=combined(questions)
            else:row['file_questions']=copy.deepcopy(questions)
            rows = [r for r in rows if r['id'] != row['id']] + [row]
        elif action in {'start', 'end'}:
            row = old
            if action == 'start':
                if row['state'] != 'idle':
                    raise learning.LearningError(409, 'Phiên thực hành đã mở hoặc đã kết thúc.')
                if row['type'] == 'programming' and not code_runner.ready():
                    raise learning.LearningError(503, 'Bộ chấm Docker chưa sẵn sàng.')
                if not set(row['participants']).issubset(members(course)):
                    raise learning.LearningError(409, 'Danh sách lớp đã thay đổi, cần lưu lại phiên.')
                from .question_papers import distribute
                distribute(row)
                now = datetime.now(timezone.utc)
                row.update(state='started', started_at=now.isoformat(), ends_at=(now + timedelta(minutes=row['duration_minutes'])).isoformat())
                if row['type'] == 'file':
                    data = learning.load()
                    for i, q in enumerate(row['file_questions']):
                        from .question_papers import indices
                        assigned=[sid for sid in row['participants'] if i in indices(row,sid)]
                        if not assigned:continue
                        data['assignments'].append({'id': row['id'] + '_' + str(i), 'course_id': cid, 'title': q['title'],
                            'description': q['statement'], 'created_at': utc_now(), 'due_at': row['ends_at'],
                            'max_attempts': 20, 'accepted_extensions': q['extensions'], 'participants': assigned,
                            'week_number': row['week_number'], 'practical_id': row['id']})
                    write_json('learning.json', data)
            else:
                if row['state'] == 'idle':
                    raise learning.LearningError(409, 'Phiên chưa được mở.')
                row.update(state='ended', ends_at=utc_now())
                attempts = read_json('programming_attempts.json', {})
                for key, attempt in attempts.items():
                    if key.startswith(row['id'] + ':'):
                        attempt['ends_at'] = min(attempt['ends_at'], row['ends_at'])
                write_json('programming_attempts.json', attempts)
                data = learning.load()
                for assignment in data['assignments']:
                    if assignment.get('practical_id') == row['id']:
                        assignment['due_at'] = row['ends_at']
                write_json('learning.json', data)
        else:
            raise learning.LearningError(400, 'Thao tác không hợp lệ.')
        write_json(SESSIONS, rows)
        audit('learning.practical_' + action, session['user_id'], ip, {'id': row['id']})
        return {'ok': True, 'id': row['id']}


def combined(questions):
    languages = set(questions[0]['programming']['languages'])
    problems = []
    for q in questions:
        languages.intersection_update(q['programming']['languages'])
        problems.extend(copy.deepcopy(q['programming']['problems']))
    if not languages:
        raise learning.LearningError(400, 'Các câu phải có ngôn ngữ chạy tương thích.')
    # Revalidate the combined budget and preserve each nv09 template/test code.
    return configuration({'languages': ','.join(sorted(languages)), 'problems': json.dumps(problems)})


def code_rows():
    result=[r for r in sessions() if r['type']=='programming']
    courses = learning.load()['courses']
    students = read_json('students.json')
    for q in bank():
        if q['response_type']!='code' or not q.get('published') or q.get('archived'):continue
        for course in linked_courses(q, courses):
            result.append({**copy.deepcopy(q),'id':practice_id(q,course['id']),'course_id':course['id'],'practice':True,
                'type':'programming','state':'started','activity_type':'practice','assessment_type':'test',
                'duration_minutes':0,'ends_at':FUTURE,'participants':members(course, students),
                'description':q.get('statement','')+'\nBài tự luyện, không tính điểm khóa học.'})
    return result


def decorate_snapshot(result, session):
    if session['role'] == 'admin':
        from .question_papers import listing
        result['question_papers']=listing()
        result['question_bank'] = bank()
        result['practicals'] = sessions()
        result['code_activities'] = code_rows()
    else:
        sid = session['user_id']
        result['practicals'] = [{k: r.get(k) for k in ('id', 'title', 'course_id', 'response_type', 'duration_minutes', 'state', 'started_at', 'ends_at', 'week_number')}
            for r in sessions() if r['state'] != 'idle' and sid in r['participants'] and r['course_id'] in {c['id'] for c in result['courses']}]
    return result


def homework_scores(course_id, sid, *, records=None, practical_sessions=None):
    from . import programming
    records = records if records is not None else programming.rows()
    scores = []
    for row in (practical_sessions if practical_sessions is not None else sessions()):
        if row['type'] != 'programming' or row['course_id'] != course_id or row['state'] == 'idle' or sid not in row['participants']:
            continue
        marks = []
        from .question_papers import indices
        assigned=indices(row,sid)
        for index in assigned:
            p=row['programming']['problems'][index]
            attempts = [s for s in records if s['exam_id'] == row['id'] and s['student_id'] == sid and s['problem_index'] == index]
            graded = [programming.public_submission(s, True)['effective_score'] for s in attempts]
            graded = [v for v in graded if v is not None]
            marks.append(max(graded) if graded else 0 if not attempts and row['state'] == 'ended' else None)
        if all(v is not None for v in marks):
            scores.append(round(10 * sum(marks) / sum(row['programming']['problems'][i]['points'] for i in assigned), 2))
        elif row['state'] == 'ended' or any(v is not None for v in marks):
            scores.append(None)
    return scores


def run_sample(session, form, ip):
    from . import programming, submission_rate
    sid = session['user_id']
    with learning.LOCK:
        row = programming.exam(form.get('exam_id'))
        if not programming.eligible(row, sid):
            raise learning.LearningError(403, 'Bạn không được giao bài này.')
        if row.get('activity_type') not in {'practice', 'practical'}:
            raise learning.LearningError(400, 'Chạy thử dành cho bài tập code.')
        attempt = read_json('programming_attempts.json', {}).get(row['id'] + ':' + sid)
        course = learning.find(learning.load(), 'courses', row['course_id'])
        if course['status'] == 'completed' or row['state'] != 'started' or not attempt or attempt.get('status') == 'submitted' or learning.date_value(row['ends_at']) <= datetime.now(timezone.utc):
            raise learning.LearningError(409, 'Bài chưa mở hoặc đã hết thời gian.')
        index = exam_catalog.integer(form.get('problem_index'), 'Bài toán', 0, len(row['programming']['problems']) - 1)
        from .question_papers import indices
        if index not in indices(row,sid):raise learning.LearningError(403,'Câu hỏi không thuộc đề được phát cho bạn.')
        problem = copy.deepcopy(row['programming']['problems'][index])
        language, source = form.get('language'), form.get('source', '')
        if language not in row['programming']['languages'] or problem.get('language') and language != problem['language']:
            raise learning.LearningError(400, 'Ngôn ngữ không được phép.')
        if not isinstance(source, str) or not source.strip() or len(source.encode('utf-8')) > 100000:
            raise learning.LearningError(400, 'Mã nguồn phải từ 1 đến 100.000 byte.')
        problem['tests'] = [t for t in problem['tests'] if t['sample']]
        if not problem['tests']:
            raise learning.LearningError(400, 'Giảng viên chưa công bố test mẫu.')
    if not code_runner.ready():
        raise learning.LearningError(503, 'Bộ chấm Docker chưa sẵn sàng.')
    if not _runs.acquire(blocking=False):
        raise learning.LearningError(429, 'Đang có hai lượt chạy thử; hãy đợi kết quả.')
    try:
        with submission_rate.guard('run:' + sid):
            try:
                result = code_runner.judge(source.encode('utf-8'), language, problem)
            except (ValueError, RuntimeError) as exc:
                raise learning.LearningError(503, 'Bộ chấm chưa chạy được; hãy thử lại sau.') from exc
        result.pop('score', None)
        result.pop('private_compile_log', None)
        return {'ok': True, 'result': result}
    finally:
        _runs.release()
