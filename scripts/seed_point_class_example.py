"""Add one repeat-safe Java OOP practice problem for class-contract grading.

Run while the web server is stopped: python -m scripts.seed_point_class_example
"""
import json

from app import exercise_bank, learning, storage
from app.runtime import data_lease


TITLE = '[Mẫu OOP] Point: thuộc tính và phương thức'
COURSE_CODE = 'JAVA-OOP-2026'
ADMIN = {'role': 'admin', 'user_id': 'admin'}


def test(code, output, sample=False):
    return {'input': '', 'output': output, 'test_code': code,
            'sample': sample, 'feedback_visibility': 'sample'}


TESTS = [
    test('''boolean ok;
try {
    java.lang.reflect.Field x = Point.class.getDeclaredField("positionX");
    java.lang.reflect.Field y = Point.class.getDeclaredField("positionY");
    ok = x.getType() == double.class && y.getType() == double.class
        && java.lang.reflect.Modifier.isPrivate(x.getModifiers())
        && java.lang.reflect.Modifier.isPrivate(y.getModifiers());
} catch (NoSuchFieldException error) { ok = false; }
System.out.print(ok);''', 'true', True),
    test('''boolean ok;
try {
    ok = java.lang.reflect.Modifier.isPublic(Point.class.getConstructor().getModifiers())
        && java.lang.reflect.Modifier.isPublic(Point.class.getConstructor(double.class, double.class).getModifiers());
} catch (NoSuchMethodException error) { ok = false; }
System.out.print(ok);''', 'true'),
    test('Point point = new Point(); System.out.print(point.getPositionX() + "," + point.getPositionY());', '0.0,0.0', True),
    test('Point point = new Point(2.5, -3.0); System.out.print(point.getPositionX() + "," + point.getPositionY());', '2.5,-3.0'),
    test('Point point = new Point(); point.setPositionX(-4.0); point.setPositionY(1.5); System.out.print(point);', 'Point(-4.0,1.5)'),
    test('Point point = new Point(1.0, 2.0); point.moveLeft(3.0); point.moveRight(1.0); point.moveUp(4.0); point.moveDown(2.0); System.out.print(point);', 'Point(-1.0,4.0)'),
    test('System.out.print(Point.getDistance(0, 0, 3, 4));', '5.0'),
]


def main():
    with data_lease(storage.DATA_DIR):
        storage.initialize()
        course = next((c for c in learning.load()['courses'] if c.get('code') == COURSE_CODE), None)
        if not course:
            raise RuntimeError('Không tìm thấy khóa Java OOP mẫu.')
        old = next((q for q in exercise_bank.bank() if q.get('title') == TITLE and course['id'] in q.get('course_ids', [])), None)
        if old:
            print(json.dumps({'status': 'already-present', 'question_id': old['id']}))
            return
        problem = {
            'title': 'Cài đặt lớp Point',
            'statement': ('Nộp một file Point.java với package lecture.demo và public class Point. '
                          'Khai báo hai thuộc tính private double positionX, positionY. '
                          'Viết constructor mặc định đưa cả hai về 0.0 và constructor nhận x, y; '
                          'getter/setter cho hai thuộc tính; moveLeft, moveRight, moveUp, moveDown; '
                          'static getDistance(x, y, x1, y1); toString theo dạng Point(x,y). '
                          'PointTemplate chỉ là gợi ý cấu trúc, không nộp cùng file. '
                          'Chưa có quy tắc min/max nên bài này không kiểm tra giới hạn tọa độ.'),
            'answer_kind': 'class', 'language': 'java', 'points': 100,
            'time_limit_ms': 2000, 'memory_limit_mb': 256, 'checker': 'exact',
            'tests': TESTS,
        }
        saved = exercise_bank.manage_question(ADMIN, 'save', {
            'title': TITLE, 'statement': problem['statement'],
            'course_ids': json.dumps([course['id']]), 'purpose': 'practice',
            'response_type': 'code', 'languages': 'java',
            'problems': json.dumps([problem], ensure_ascii=False),
            'week_number': '3',
        }, '127.0.0.1')
        exercise_bank.manage_question(ADMIN, 'publish', {'id': saved['id']}, '127.0.0.1')
        print(json.dumps({'status': 'created', 'question_id': saved['id'], 'tests': len(TESTS)}))


if __name__ == '__main__':
    main()
