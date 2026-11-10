import os
import unittest
from app import code_templates as templates, code_runner


class TemplateTests(unittest.TestCase):
    def test_hidden_test_code_and_private_diagnostics_never_reach_student(self):
        from app.programming import public_submission
        grade={'score':0,'private_compile_log':'secret wrapper','tests':[{'sample':False,'test_code':'secret test','input':'secret','expected':'secret','actual':'secret','stderr':'secret','feedback_visibility':'hide'}]}
        row={'result':grade,'grading_history':[{'result':grade}]}
        student=public_submission(row)
        self.assertNotIn('secret',str(student))
        self.assertIn('secret',str(public_submission(row,admin=True)))

    def test_http_configuration_roundtrip(self):
        import json
        from tests.test_learning import LearningTests
        from app import exam_catalog
        fixture=LearningTests()
        try:
            fixture.setUp()
            spec={'title':'Method','answer_kind':'method','language':'java','template':'','tests':[{'input':'','output':'5','sample':True,'test_code':'System.out.println(add(2,3));','feedback_visibility':'hide'}]}
            form={'course_id':fixture.course(),'title':'Template exam','type':'programming','languages':'java','problems':json.dumps([spec])}
            status,saved=fixture.request('/api/admin/exam-configurations/save',form=form)
            self.assertEqual(status,200,saved)
            actual=next(x for x in exam_catalog.listing() if x['id']==saved['id'])['programming']['problems'][0]
            self.assertEqual(actual['answer_kind'],'method')
            self.assertEqual(actual['tests'][0]['test_code'],spec['tests'][0]['test_code'])
            self.assertEqual(actual['tests'][0]['feedback_visibility'],'hide')
            spec['tests'][0]['test_code']=''
            form['problems']=json.dumps([spec])
            self.assertEqual(fixture.request('/api/admin/exam-configurations/save',form=form)[0],400)
        finally:
            fixture.doCleanups()

    def test_markers_in_answer_are_literal(self):
        source=b'print("{{ TEST.testcode }}")'
        result,_=templates.build(source,'python',{'answer_kind':'method','template':templates.ANSWER+'\n'+templates.TEST},{'test_code':'print(2)'})
        self.assertIn(source,result)

    def test_public_java_class_keeps_its_filename(self):
        source=b'public class Product { public int price(){return 7;} }'
        generated,extra=templates.build(source,'java',{'answer_kind':'class'},{'test_code':'System.out.println(new Product().price());'})
        self.assertEqual(extra,{'Product.java':source})
        self.assertIn(b'public class Main',generated)

    def test_visibility_is_independent_from_examples(self):
        self.assertFalse(templates.visible({'sample':True,'feedback_visibility':'hide'}))
        self.assertTrue(templates.visible({'sample':False,'feedback_visibility':'show'}))
        self.assertFalse(templates.visible({'verdict':'WA','feedback_visibility':'hide_if_fail'}))

    def test_missing_test_code_is_rejected(self):
        with self.assertRaises(ValueError):
            templates.validate({'answer_kind':'method','tests':[{}]})


@unittest.skipUnless(os.getenv('CSS_JUDGE_TESTS')=='1','Requires Docker')
class TemplateDockerTests(unittest.TestCase):
    def run_case(self,language,kind,source,code,expected,verdict='AC'):
        problem={'answer_kind':kind,'points':10,'checker':'tokens','time_limit_ms':2000,'memory_limit_mb':256,'tests':[{'input':'','output':expected,'sample':True,'test_code':code}]}
        result=code_runner.judge(source.encode(),language,problem)
        self.assertEqual(result['verdict'],verdict,result)

    def test_java_class(self):
        self.run_case('java','class','public class Product { public int price(){return 7;} }','System.out.println(new Product().price());','7')

    def test_java_inheritance_in_one_source_file(self):
        source='abstract class Person { abstract String info(); } public class Student extends Person { String info(){return "ok";} }'
        self.run_case('java','class',source,'Person p = new Student(); System.out.println(p.info());','ok')

    def test_java_method(self):
        self.run_case('java','method','int add(int a,int b){return a+b;}','System.out.println(add(2,3));','5')

    def test_python_function(self):
        self.run_case('python','method','def add(a,b): return a+b','print(add(2,3))','5')

    def test_cpp_class(self):
        self.run_case('cpp','class','class Product { public: int price(){return 7;} };','cout << Product().price();','7')

    def test_wrong_result(self):
        self.run_case('python','method','def add(a,b): return 0','print(add(2,3))','5','WA')

    def test_compile_error(self):
        self.run_case('java','method','invalid source','System.out.println(add(2,3));','5','CE')
