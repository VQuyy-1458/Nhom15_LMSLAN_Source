import io
import json
import os
import unittest
import zipfile

from app import code_runner, code_templates, exam_catalog
from app.java_sources import submission, teacher_files
from app.oop_rubric import tests as rubric_tests, validate


class OopRubricTests(unittest.TestCase):
    def rubric(self):
        return validate({'version': 1, 'class_name': 'Counter', 'criteria': [
            {'kind': 'class', 'access': 'public', 'points': 1},
            {'kind': 'field', 'name': 'value', 'type': 'int', 'access': 'private', 'static': False, 'points': 2},
            {'kind': 'constructor', 'parameters': ['int'], 'access': 'public', 'points': 1},
            {'kind': 'method', 'name': 'add', 'parameters': ['int'], 'return_type': 'int', 'access': 'public', 'points': 2},
        ]}, 10, 'java', 'class')

    def problem(self):
        return {'answer_kind': 'class', 'language': 'java', 'points': 10,
                'time_limit_ms': 2000, 'memory_limit_mb': 256, 'checker': 'tokens',
                'oop_rubric': self.rubric(), 'tests': [
                    {'input': '', 'output': '5', 'sample': True,
                     'test_code': 'System.out.print(new Counter(3).add(2));',
                     'points': 4, 'category': 'behavior', 'criterion': 'add'}]}

    def test_generated_structure_and_weights(self):
        problem = self.problem()
        rows, weights = code_runner.test_weights(problem)
        self.assertEqual(weights, [1, 2, 1, 2, 4])
        self.assertEqual(len(rows), 5)
        self.assertIn('getDeclaredField("value")', rows[1]['test_code'])
        self.assertIn('getDeclaredConstructors()', rows[2]['test_code'])
        self.assertIn('getDeclaredMethods()', rows[3]['test_code'])
        source, extra = code_templates.build(b'public class Counter {}', 'java', problem, rows[0])
        self.assertIn(b'Class.forName("Counter", false', source)
        self.assertIn('Counter.java', extra)

    def test_existing_problem_schema_keeps_oop_configuration(self):
        problem = self.problem()
        problem['title'] = 'Counter OOP'
        problem['statement'] = 'Viết lớp Counter.'
        problem['starter_code'] = 'public class Counter { }'
        problem['provided_files'] = [{'filename': 'Helper.java', 'source': 'class Helper {}'}]
        problem['accept_java_zip'] = True
        saved = exam_catalog.validate_programming({'languages': 'java', 'problems': json.dumps([problem])})['problems'][0]
        self.assertEqual(saved['oop_rubric']['class_name'], 'Counter')
        self.assertEqual(saved['starter_code'], problem['starter_code'])
        self.assertEqual(saved['provided_files'], problem['provided_files'])
        self.assertTrue(saved['accept_java_zip'])
        self.assertEqual(saved['tests'][0]['points'], 4)

    def test_rejects_invalid_and_overweighted_rubric(self):
        bad = {'version': 1, 'class_name': 'Counter', 'criteria': [
            {'kind': 'field', 'name': 'value', 'type': 'int', 'access': 'private', 'points': 11}]}
        with self.assertRaises(ValueError): validate(bad, 10, 'java', 'class')
        bad['criteria'][0]['points'] = 2
        bad['criteria'][0]['name'] = 'value); System.exit(0);'
        with self.assertRaises(ValueError): validate(bad, 10, 'java', 'class')

    def test_zip_flat_names_and_teacher_collision(self):
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as file:
            file.writestr('Counter.java', 'public class Counter {}')
            file.writestr('Helper.java', 'class Helper {}')
        main, extra = submission(archive.getvalue(), 'Counter')
        self.assertIn(b'public class Counter', main)
        self.assertEqual(set(extra), {'Helper.java'})
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as file:
            file.writestr('../Counter.java', 'public class Counter {}')
        with self.assertRaises(ValueError): submission(archive.getvalue(), 'Counter')
        with self.assertRaises(ValueError): teacher_files([{'filename': 'Counter.java', 'source': 'class Counter {}'}], 'Counter')


@unittest.skipUnless(os.getenv('CSS_JUDGE_TESTS') == '1', 'Docker judge opt-in')
class OopRubricDockerTests(OopRubricTests):
    def test_partial_credit_for_public_field(self):
        problem = self.problem()
        source = b'public class Counter { private int value; public Counter(int n){value=n;} public int add(int n){return value+n;} }'
        correct = code_runner.judge(source, 'java', problem)
        wrong = code_runner.judge(source.replace(b'private int', b'public int'), 'java', problem)
        self.assertEqual((correct['verdict'], correct['score']), ('AC', 10))
        self.assertEqual((wrong['verdict'], wrong['score']), ('WA', 8))
        self.assertEqual(wrong['tests'][-1]['verdict'], 'AC')
