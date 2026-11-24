import json
import os
import unittest

from app import code_runner, exam_catalog
from scripts.seed_bank_account_oop_demo import PROBLEM, SOURCE, WRONG_PUBLIC_FIELD, WRONG_WITHDRAWAL


class BankAccountOopDemoTests(unittest.TestCase):
    def problem(self):
        return exam_catalog.validate_programming({
            'languages': 'java',
            'problems': json.dumps([PROBLEM]),
        })['problems'][0]

    def test_problem_has_full_weighted_structure_and_behavior_coverage(self):
        problem = self.problem()
        tests, weights = code_runner.test_weights(problem)

        self.assertEqual(len(problem['oop_rubric']['criteria']), 7)
        self.assertEqual(len(problem['tests']), 6)
        self.assertEqual(sum(weights), 100)
        self.assertEqual(sum(test['points'] for test in tests if test['category'] == 'structure'), 40)
        self.assertEqual(sum(test['points'] for test in tests if test['category'] == 'behavior'), 60)


@unittest.skipUnless(os.getenv('CSS_JUDGE_TESTS') == '1', 'Requires Docker')
class BankAccountOopDemoDockerTests(BankAccountOopDemoTests):
    def test_judge_distinguishes_correct_structure_and_behavior(self):
        problem = self.problem()
        correct = code_runner.judge(SOURCE.encode(), 'java', problem)
        wrong_structure = code_runner.judge(WRONG_PUBLIC_FIELD.encode(), 'java', problem)
        wrong_behavior = code_runner.judge(WRONG_WITHDRAWAL.encode(), 'java', problem)

        self.assertEqual((correct['verdict'], correct['score']), ('AC', 100), correct)
        self.assertEqual((wrong_structure['verdict'], wrong_structure['score']), ('WA', 90), wrong_structure)
        self.assertEqual(wrong_structure['tests'][-1]['verdict'], 'AC')
        self.assertEqual((wrong_behavior['verdict'], wrong_behavior['score']), ('WA', 90), wrong_behavior)
        self.assertEqual(wrong_behavior['tests'][-1]['verdict'], 'WA')
