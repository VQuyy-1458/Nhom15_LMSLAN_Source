"""Explicit weekly learning plans and shared resource placement."""
import copy
import json
import secrets
from . import learning
from .storage import atomic_transaction, write_json, utc_now, audit


def week_number(form):
    return learning.integer(form, 'week_number', 0, 0, 52)


def ids(form, key):
    try:
        value = json.loads(form.get(key, '[]'))
    except (TypeError, ValueError):
        raise learning.LearningError(400, 'Danh sách nội dung không hợp lệ.')
    if not isinstance(value, list) or len(value) > 100 or any(not isinstance(x, str) for x in value):
        raise learning.LearningError(400, 'Danh sách nội dung không hợp lệ.')
    return list(dict.fromkeys(value))


def save(session, form, ip):
    if session['role'] != 'admin':
        raise learning.LearningError(403, 'Chỉ giảng viên được sửa nội dung theo tuần.')
    with learning.LOCK, atomic_transaction():
        data = learning.load()
        course = learning.course_access(data, form.get('course_id'), session, write=True)
        number = learning.integer(form, 'week_number', 1, 1, 52)
        rows = data.setdefault('course_weeks', [])
        old = next((r for r in rows if r['course_id'] == course['id'] and r['week_number'] == number), None)
        row = {'id': old['id'] if old else secrets.token_hex(10), 'course_id': course['id'],
               'week_number': number, 'title': learning.text(form, 'title'),
               'lesson_text': learning.text(form, 'lesson_text', 20000, False),
               'reading_text': learning.text(form, 'reading_text', 20000, False),
               'created_at': old['created_at'] if old else utc_now(), 'updated_at': utc_now()}
        for key, collection in [('material_ids', 'materials'), ('assignment_ids', 'assignments'), ('announcement_ids', 'events')]:
            row[key] = ids(form, key)
            for item_id in row[key]:
                item = learning.find(data, collection, item_id)
                if item['course_id'] != course['id'] or key == 'announcement_ids' and item.get('kind') != 'announcement':
                    raise learning.LearningError(400, 'Nội dung phải thuộc khóa học và đúng loại.')
        from . import exercise_bank
        available = {r['id']: r for r in exercise_bank.code_rows()}
        row['activity_ids'] = ids(form, 'activity_ids')
        if any(k not in available or available[k]['course_id'] != course['id'] for k in row['activity_ids']):
            raise learning.LearningError(400, 'Bài code không thuộc khóa học.')
        data['course_weeks'] = [r for r in rows if r['id'] != row['id']] + [row]
        write_json('learning.json', data)
        audit('learning.week_saved', session['user_id'], ip, {'id': row['id']})
        return {'ok': True, 'id': row['id']}


def snapshot(data, visible):
    """Never disclose references to content the student's snapshot cannot see."""
    allowed = {key: {r['id'] for r in visible.get(key, [])} for key in ('courses', 'materials', 'assignments', 'events')}
    rows = copy.deepcopy(data.get('course_weeks', []))
    result = []
    for row in rows:
        if row['course_id'] not in allowed['courses']:
            continue
        for key, collection in [('material_ids', 'materials'), ('assignment_ids', 'assignments'), ('announcement_ids', 'events')]:
            row[key] = [k for k in row.get(key, []) if k in allowed[collection]]
        result.append(row)
    return result


def resource_visible(row, sid):
    return not row.get('archived') and row.get('published', True) and (row.get('participants') is None or sid in row['participants'])
