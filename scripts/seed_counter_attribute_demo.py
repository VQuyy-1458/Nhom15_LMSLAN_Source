"""Create a Java class-grading demo and two contrasting submission files.

Run with the web server stopped: python -m scripts.seed_counter_attribute_demo
"""
import json
from pathlib import Path

from app import exercise_bank, learning, storage
from app.runtime import data_lease


ROOT = Path(__file__).resolve().parents[1]
COURSE_CODE = 'JAVA-OOP-2026'
TITLE = '[Demo] Counter - chấm cấu trúc và hành vi'
SOURCE = '''package lecture.practice;

public class Counter {
    private int value;

    public Counter() { this.value = 0; }
    public Counter(int initial) { this.value = Math.max(0, initial); }
    public int getValue() { return value; }
    public void setValue(int next) { if (next >= 0) value = next; }
    public void increment(int step) { if (step > 0) value += step; }
    @Override public String toString() { return "Counter(" + value + ")"; }
}
'''


def test(code, expected, sample=False):
    return {'input': '', 'output': expected, 'test_code': code,
            'sample': sample, 'feedback_visibility': 'sample'}


TESTS = [
    test('''boolean valid;
try {
    java.lang.reflect.Field field = Counter.class.getDeclaredField("value");
    valid = field.getType() == int.class
        && java.lang.reflect.Modifier.isPrivate(field.getModifiers())
        && !java.lang.reflect.Modifier.isStatic(field.getModifiers());
} catch (NoSuchFieldException error) { valid = false; }
System.out.print(valid);''', 'true', True),
    test('System.out.print(new Counter().getValue() + "|" + new Counter(4).getValue());', '0|4', True),
    test('Counter counter = new Counter(-3); counter.setValue(4); counter.setValue(-2); System.out.print(counter.getValue());', '4'),
    test('Counter counter = new Counter(2); counter.increment(3); counter.increment(-5); System.out.print(counter.getValue());', '5'),
    test('Counter counter = new Counter(5); System.out.print(counter.toString());', 'Counter(5)'),
]


def write_examples():
    folder = ROOT / 'demo-inputs' / 'counter-grade-demo'
    for label, source in [('correct', SOURCE), ('wrong-public-attribute', SOURCE.replace('private int value;', 'public int value;'))]:
        destination = folder / label / 'Counter.java'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source, encoding='utf-8')
    return folder


def main():
    with data_lease(storage.DATA_DIR):
        storage.initialize()
        course = next((row for row in learning.load()['courses'] if row.get('code') == COURSE_CODE), None)
        if not course:
            raise RuntimeError('Không tìm thấy khóa Java OOP mẫu.')
        old = next((row for row in exercise_bank.bank()
                    if row.get('title') == TITLE and course['id'] in row.get('course_ids', [])), None)
        if old:
            print(json.dumps({'status': 'already-present', 'question_id': old['id'],
                              'samples': str(write_examples())}))
            return
        problem = {
            'title': 'Counter - class có thuộc tính private',
            'statement': ('Chỉ nộp Counter.java, package lecture.practice, không viết main. '
                          'Class Counter có private int value; constructor mặc định đặt 0; '
                          'constructor Counter(int initial) đặt max(0, initial). '
                          'getValue trả value. setValue(next) chỉ đổi value nếu next >= 0. '
                          'increment(step) chỉ cộng nếu step > 0. '
                          'toString trả Counter(value). Mỗi yêu cầu được chấm riêng. '
                          'Hai mã mẫu ở demo-inputs/counter-grade-demo có output giống nhau, '
                          'nhưng bản wrong-public-attribute khai báo sai quyền truy cập.'),
            'answer_kind': 'class', 'language': 'java', 'points': 100,
            'time_limit_ms': 2000, 'memory_limit_mb': 256,
            'checker': 'exact', 'tests': TESTS,
        }
        result = exercise_bank.manage_question({'role': 'admin', 'user_id': 'admin'}, 'save', {
            'title': TITLE, 'statement': problem['statement'],
            'course_ids': json.dumps([course['id']]), 'purpose': 'practice',
            'response_type': 'code', 'languages': 'java',
            'problems': json.dumps([problem], ensure_ascii=False),
            'week_number': '3',
        }, '127.0.0.1')
        exercise_bank.manage_question({'role': 'admin', 'user_id': 'admin'}, 'publish',
                                      {'id': result['id']}, '127.0.0.1')
        print(json.dumps({'status': 'created', 'question_id': result['id'],
                          'tests': len(TESTS), 'samples': str(write_examples())}))


if __name__ == '__main__':
    main()
