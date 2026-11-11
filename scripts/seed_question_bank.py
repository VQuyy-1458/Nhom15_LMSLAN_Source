"""Add validated question-bank examples without replacing existing content."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import classification, exam_catalog
from app.storage import read_json, write_json, atomic_transaction, utc_now, audit


def main():
    teachers = read_json('teachers.json', {})
    courses = read_json('learning.json')['courses']
    course = next((c for c in courses if c.get('status') == 'active' and any(
        teachers.get(t, {}).get('active', False) for t in c.get('teacher_ids', []))), None)
    if not course:
        raise SystemExit('Cần ít nhất một khóa học đang hoạt động đã phân công giáo viên.')
    owner = next(t for t in course['teacher_ids'] if teachers.get(t, {}).get('active', False))
    # Each sample includes explicit input constraints and independently checked expected output.
    examples = [
        ('sum', 'Tổng hai số nguyên', 'easy', 'Nhập xuất và toán cơ bản',
         'Đọc hai số nguyên a, b trên một hoặc nhiều dòng, |a|, |b| <= 10^9. In tổng a + b. Input luôn có đủ hai số.',
         ['1 2', '0 0', '-5 8', '-30 0', '1000000000 1000000000', '-1000000000 -1000000000'],
         lambda s: str(sum(map(int, s.split())))),
        ('max', 'Giá trị lớn nhất trong dãy', 'easy', 'Mảng và vòng lặp',
         'Dòng đầu là n (1 <= n <= 100000). Tiếp theo là n số nguyên có giá trị tuyệt đối <= 10^9. In giá trị lớn nhất. Các số có thể nằm trên nhiều dòng.',
         ['5\n1 7 3 2 4', '1\n-9', '4\n-8 -2 -10 -3', '3\n5 5 5', '2\n-1000000000 1000000000'],
         lambda s: str(max(list(map(int, s.split()))[1:]))),
        ('even', 'Đếm phần tử chẵn', 'easy', 'Mảng và vòng lặp',
         'Đọc n (1 <= n <= 100000), sau đó n số nguyên có giá trị tuyệt đối <= 10^9. In số phần tử chia hết cho 2; số 0 là số chẵn.',
         ['5\n1 2 3 4 6', '1\n0', '4\n-4 -3 -2 -1', '3\n1 3 5', '4\n2 2 2 2'],
         lambda s: str(sum(x % 2 == 0 for x in list(map(int, s.split()))[1:]))),
        ('palindrome', 'Chuỗi đối xứng', 'easy', 'Xử lý chuỗi',
         'Đọc một chuỗi không rỗng chỉ gồm chữ cái tiếng Anh viết thường, độ dài tối đa 100000. In YES nếu đọc xuôi và ngược giống nhau, ngược lại in NO.',
         ['abba', 'abc', 'a', 'aaaaa', 'abca', 'racecar'],
         lambda s: 'YES' if s == s[::-1] else 'NO'),
        ('gcd', 'Ước chung lớn nhất', 'medium', 'Số học',
         'Đọc hai số nguyên a, b, |a|, |b| <= 10^9, không đồng thời bằng 0. In ước chung lớn nhất không âm của a và b. Có thể sử dụng thuật toán Euclid.',
         ['12 18', '0 15', '-24 18', '17 13', '1000000000 500000000', '9 0'],
         lambda s: str(__import__('math').gcd(*map(int, s.split())))),
        ('distinct', 'Đếm giá trị phân biệt', 'medium', 'Sắp xếp và tìm kiếm',
         'Đọc n (1 <= n <= 100000), sau đó n số nguyên có giá trị tuyệt đối <= 10^9. In số giá trị khác nhau trong dãy. Mỗi giá trị chỉ được tính một lần.',
         ['6\n1 2 2 3 1 4', '1\n7', '5\n0 0 0 0 0', '5\n-2 -1 0 1 2', '4\n1000000000 -1000000000 1000000000 0'],
         lambda s: str(len(set(map(int, s.split()[1:]))))),
        ('range-sum', 'Tổng đoạn với mảng cộng dồn', 'medium', 'Mảng cộng dồn',
         'Dòng đầu gồm n và q (1 <= n, q <= 100000). Dòng tiếp theo có n số nguyên, |ai| <= 10^9. q dòng sau, mỗi dòng gồm l, r (1 <= l <= r <= n). Với mỗi truy vấn, in tổng các phần tử từ l đến r (đánh số từ 1), mỗi kết quả một dòng. Dùng số nguyên 64 bit.',
         ['5 3\n1 2 3 4 5\n1 3\n2 5\n4 4', '1 1\n-7\n1 1', '3 2\n1000000000 1000000000 1000000000\n1 3\n2 3', '4 2\n-2 0 5 -3\n1 4\n2 3'],
         range_sums),
        ('max-subarray', 'Tổng đoạn con lớn nhất', 'hard', 'Quy hoạch động',
         'Đọc n (1 <= n <= 100000), sau đó n số nguyên, |ai| <= 10^9. In tổng lớn nhất của một đoạn con liên tiếp không rỗng. Yêu cầu thuật toán O(n), dùng số nguyên 64 bit. Nếu mọi số đều âm vẫn phải chọn ít nhất một phần tử.',
         ['9\n-2 1 -3 4 -1 2 1 -5 4', '3\n-5 -2 -8', '1\n7', '3\n0 0 0', '4\n1000000000 1000000000 1000000000 1000000000', '5\n5 -10 4 3 -1'],
         max_subarray),
    ]
    with atomic_transaction():
        topics = read_json('topics.json', [])
        questions = read_json('questions.json', [])
        added = 0
        for slug, title, difficulty, topic_name, statement, inputs, solve in examples:
            qid = 'q_demo_bank_' + slug.replace('-', '_')
            if any(q['id'] == qid for q in questions):
                continue
            topic = next((t for t in topics if t['name'] == topic_name and t.get('active', True)), None)
            if not topic:
                topic = {'id': 'topic_bank_' + slug.replace('-', '_'), 'name': topic_name,
                         'active': True, 'created_at': utc_now()}
                topics.append(topic)
            tests = [{'input': value + '\n', 'output': solve(value) + '\n', 'sample': i < 2}
                     for i, value in enumerate(inputs)]
            # Include one large case to catch integer overflow and quadratic solutions.
            if slug in {'range-sum', 'max-subarray'}:
                # Keep input under the 100,000-character test-case payload limit.
                value = ('8000 1\n' + ' '.join(['1000000000'] * 8000) + '\n1 8000'
                         if slug == 'range-sum' else '8000\n' + ' '.join(['1000000000'] * 8000))
                tests.append({'input': value + '\n', 'output': solve(value) + '\n', 'sample': False})
            config = exam_catalog.validate_programming({'languages': 'c,cpp,java,python', 'problems': json.dumps([
                {'title': title, 'statement': statement, 'points': 100, 'time_limit_ms': 1000,
                 'memory_limit_mb': 256, 'checker': 'tokens', 'tests': tests}])})
            questions.append({'id': qid, 'title': title, 'course_id': course['id'], 'created_by': owner,
                              'created_at': utc_now(), 'updated_at': utc_now(), 'published': True,
                              'content_type': 'question', 'topic_ids': [topic['id']], 'difficulty': difficulty,
                              'classification_languages': ['c', 'cpp', 'java', 'python'], 'programming': config})
            added += 1
        write_json('topics.json', topics)
        write_json('questions.json', questions)
        audit('classification.seed-question-bank', owner, None, {'added': added, 'course_id': course['id']})
    visible = classification.snapshot({'role': 'teacher', 'user_id': owner})
    assert sum(q['id'].startswith('q_demo_bank_') for q in visible['content']) >= 8
    print(json.dumps({'added': added, 'course': course['name'], 'owner': owner,
                      'questions': len(questions), 'test_cases': sum(len(q['programming']['problems'][0]['tests'])
                      for q in questions if q['id'].startswith('q_demo_bank_'))}, ensure_ascii=False))


def range_sums(value):
    values = list(map(int, value.split()))
    n, q = values[:2]
    prefix = [0]
    for x in values[2:2+n]:
        prefix.append(prefix[-1] + x)
    queries = values[2+n:]
    return '\n'.join(str(prefix[queries[2*i+1]] - prefix[queries[2*i]-1]) for i in range(q))


def max_subarray(value):
    values = list(map(int, value.split()))[1:]
    current = best = values[0]
    for x in values[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return str(best)


if __name__ == '__main__':
    main()
