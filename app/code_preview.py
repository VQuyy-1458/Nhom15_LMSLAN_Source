"""Bounded, non-persistent teacher trials of unsaved question configurations."""
import json
import threading
from . import code_runner, code_templates, learning

_slots = threading.BoundedSemaphore(2)


def run(form):
    try:
        problem = json.loads(form.get('problem', '{}'))
        source = form.get('source', '')
        language = form.get('language', '')
        if language not in code_runner.LANGUAGES or not isinstance(problem, dict):
            raise ValueError('Chọn ngôn ngữ hợp lệ.')
        if not isinstance(source, str) or not source.strip() or len(source.encode('utf8')) > 100000:
            raise ValueError('Đáp án thử cần có nội dung, tối đa 100 KB.')
        if problem.get('language') and language != problem['language']:
            raise ValueError('Ngôn ngữ không khớp mã kiểm thử.')
        for key, low, high in [('points',1,1000),('time_limit_ms',100,30000),('memory_limit_mb',16,2048)]:
            problem[key] = int(problem.get(key, {'points':100,'time_limit_ms':1000,'memory_limit_mb':256}[key]))
            if not low <= problem[key] <= high: raise ValueError('Giới hạn chấm không hợp lệ.')
        if problem.get('checker','tokens') not in {'tokens','exact','json'}: raise ValueError('Cách so khớp không hợp lệ.')
        problem.setdefault('checker','tokens')
        tests = problem.get('tests')
        if not isinstance(tests,list) or not 1 <= len(tests) <= 100: raise ValueError('Cần 1–100 test.')
        for test in tests:
            if not isinstance(test,dict): raise ValueError('Test không hợp lệ.')
            for key in ('input','output','test_code'):
                value = test.setdefault(key,'')
                if not isinstance(value,str) or len(value)>100000: raise ValueError('Dữ liệu test không hợp lệ.')
            test['sample'] = test.get('sample') is True
        code_templates.validate(problem)
        if not code_runner.budget_valid(problem): raise ValueError('Cấu hình vượt ngân sách chấm.')
    except (ValueError,TypeError,KeyError) as exc:
        raise learning.LearningError(400,str(exc)) from exc
    if not _slots.acquire(blocking=False):
        raise learning.LearningError(429,'Đang chạy hai lượt chấm thử. Hãy đợi kết quả.')
    try:
        return code_runner.judge(source.encode('utf8'),language,problem)
    except (ValueError,RuntimeError) as exc:
        raise learning.LearningError(503,str(exc)) from exc
    finally:
        _slots.release()
