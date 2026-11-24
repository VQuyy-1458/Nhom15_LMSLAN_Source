"""Seed a complete Java OOP class-grading demo into the Java course.

Run while the web server is stopped: python -m scripts.seed_bank_account_oop_demo
"""
import copy
import json
from pathlib import Path

from app import exercise_bank, learning, storage
from app.runtime import data_lease


ROOT = Path(__file__).resolve().parents[1]
COURSE_CODE = 'JAVA-OOP-2026'
TITLE = '[Demo OOP] BankAccount - chấm cấu trúc và hành vi'
ADMIN = {'role': 'admin', 'user_id': 'admin'}

SOURCE = '''public class BankAccount {
    private double balance;

    public BankAccount() {
        this.balance = 0.0;
    }

    public BankAccount(double initialBalance) {
        this.balance = Math.max(0.0, initialBalance);
    }

    public double getBalance() {
        return balance;
    }

    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }

    public boolean withdraw(double amount) {
        if (amount <= 0 || amount > balance) {
            return false;
        }
        balance -= amount;
        return true;
    }
}
'''
WRONG_PUBLIC_FIELD = SOURCE.replace('private double balance;', 'public double balance;')
WRONG_WITHDRAWAL = SOURCE.replace(
    'if (amount <= 0 || amount > balance) {',
    'if (amount <= 0) {',
)


def test(code, output, points, sample=False):
    return {
        'input': '',
        'output': output,
        'test_code': code,
        'sample': sample,
        'feedback_visibility': 'sample',
        'points': points,
        'category': 'behavior',
    }


PROBLEM = {
    'title': 'BankAccount - đóng gói và giao dịch',
    'statement': (
        'Chỉ nộp file BankAccount.java, không khai báo package và không viết main. '
        'Tạo public class BankAccount với thuộc tính private double balance. '
        'Constructor mặc định đặt số dư 0; BankAccount(double initialBalance) đặt '
        'số dư bằng max(0, initialBalance). getBalance() trả về số dư. '
        'deposit(amount) chỉ cộng khi amount > 0. withdraw(amount) chỉ trừ khi '
        '0 < amount <= balance và trả về true; nếu không hợp lệ, giữ nguyên số dư '
        'và trả về false. Bài chấm riêng cấu trúc lớp/thuộc tính/phương thức (40 điểm) '
        'và hành vi (60 điểm).'
    ),
    'answer_kind': 'class',
    'language': 'java',
    'points': 100,
    'time_limit_ms': 2000,
    'memory_limit_mb': 256,
    'checker': 'exact',
    'oop_rubric': {
        'version': 1,
        'class_name': 'BankAccount',
        'criteria': [
            {'kind': 'class', 'access': 'public', 'points': 5, 'label': 'Lớp BankAccount public'},
            {'kind': 'field', 'name': 'balance', 'type': 'double', 'access': 'private',
             'static': False, 'points': 10, 'label': 'Đóng gói balance'},
            {'kind': 'constructor', 'parameters': [], 'access': 'public',
             'points': 5, 'label': 'Constructor mặc định'},
            {'kind': 'constructor', 'parameters': ['double'], 'access': 'public',
             'points': 5, 'label': 'Constructor nhận số dư'},
            {'kind': 'method', 'name': 'getBalance', 'parameters': [],
             'return_type': 'double', 'access': 'public', 'points': 5,
             'label': 'Chữ ký getBalance'},
            {'kind': 'method', 'name': 'deposit', 'parameters': ['double'],
             'return_type': 'void', 'access': 'public', 'points': 5,
             'label': 'Chữ ký deposit'},
            {'kind': 'method', 'name': 'withdraw', 'parameters': ['double'],
             'return_type': 'boolean', 'access': 'public', 'points': 5,
             'label': 'Chữ ký withdraw'},
        ],
    },
    'tests': [
        test('System.out.print(new BankAccount().getBalance());', '0.0', 10, True),
        test('System.out.print(new BankAccount(125.5).getBalance());', '125.5', 10, True),
        test('System.out.print(new BankAccount(-8).getBalance());', '0.0', 10),
        test(
            'BankAccount a=new BankAccount(100); a.deposit(25); a.deposit(0); '
            'a.deposit(-7); System.out.print(a.getBalance());',
            '125.0', 10,
        ),
        test(
            'BankAccount a=new BankAccount(100); boolean ok=a.withdraw(35); '
            'System.out.print(ok+"|"+a.getBalance());',
            'true|65.0', 10,
        ),
        test(
            'BankAccount a=new BankAccount(40); boolean z=a.withdraw(0); '
            'boolean n=a.withdraw(-2); boolean big=a.withdraw(41); '
            'System.out.print(z+"|"+n+"|"+big+"|"+a.getBalance());',
            'false|false|false|40.0', 10,
        ),
    ],
}


def write_examples():
    folder = ROOT / 'demo-inputs' / 'bank-account-oop-demo'
    samples = {
        'correct': SOURCE,
        'wrong-public-field': WRONG_PUBLIC_FIELD,
        'wrong-withdrawal': WRONG_WITHDRAWAL,
    }
    for label, source in samples.items():
        destination = folder / label / 'BankAccount.java'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source, encoding='utf-8')
    return folder


def main():
    with data_lease(storage.DATA_DIR):
        storage.initialize()
        course = next(
            (row for row in learning.load()['courses'] if row.get('code') == COURSE_CODE),
            None,
        )
        if not course:
            raise RuntimeError('Không tìm thấy khóa Java OOP mẫu.')
        old = next(
            (row for row in exercise_bank.bank()
             if row.get('title') == TITLE and course['id'] in row.get('course_ids', [])),
            None,
        )
        if old:
            print(json.dumps({
                'status': 'already-present',
                'question_id': old['id'],
                'samples': str(write_examples()),
            }, ensure_ascii=False))
            return
        problem = copy.deepcopy(PROBLEM)
        result = exercise_bank.manage_question(ADMIN, 'save', {
            'title': TITLE,
            'statement': problem['statement'],
            'course_ids': json.dumps([course['id']]),
            'purpose': 'practice',
            'response_type': 'code',
            'languages': 'java',
            'problems': json.dumps([problem], ensure_ascii=False),
            'week_number': '4',
        }, '127.0.0.1')
        exercise_bank.manage_question(ADMIN, 'publish', {'id': result['id']}, '127.0.0.1')
        print(json.dumps({
            'status': 'created',
            'question_id': result['id'],
            'structural_criteria': len(problem['oop_rubric']['criteria']),
            'behavior_tests': len(problem['tests']),
            'samples': str(write_examples()),
        }, ensure_ascii=False))


if __name__ == '__main__':
    main()
