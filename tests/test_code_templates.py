import os
import unittest
from app import code_templates as templates, code_runner


class TemplateTests(unittest.TestCase):
    def test_teacher_replace_filter_and_wrapper(self):
        template="{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\npublic class __tester__ { {{ TEST.testcode }} }"
        problem={'answer_kind':'class','template':template,'tests':[{'test_code':'void test(){}'}]}
        templates.validate(problem)
        output,_=templates.build(b'public class Product {}','java',problem,problem['tests'][0])
        self.assertIn(b'class Product {}',output)
        self.assertNotIn(b'public class Product',output)
        self.assertIn(b'public class __tester__',output)
        with self.assertRaises(ValueError):
            templates.render('{{ arbitrary_function() }}','','')

    def test_preview_http_is_admin_only_and_does_not_save(self):
        import json
        from unittest.mock import patch
        from tests.test_learning import LearningTests
        from app import code_runner
        from app.storage import read_json
        fixture=LearningTests()
        try:
            fixture.setUp()
            before=read_json('exam_catalog.json',[])
            problem={'answer_kind':'method','language':'java','tests':[{'test_code':'System.out.println(add(1,2));','output':'3'}]}
            fields={'problem':json.dumps(problem),'language':'java','source':'int add(int a,int b){return a+b;}'}
            with patch.object(code_runner,'judge',return_value={'verdict':'AC','tests':[]}) as judge:
                self.assertEqual(fixture.request('/api/admin/programming/preview',role='s1',form=fields)[0],403)
                judge.assert_not_called()
                status,result=fixture.request('/api/admin/programming/preview',form=fields)
                self.assertEqual(status,200,result)
                self.assertEqual(result['verdict'],'AC')
            self.assertEqual(before,read_json('exam_catalog.json',[]))
            fields['problem']=json.dumps({'tests':[]})
            self.assertEqual(fixture.request('/api/admin/programming/preview',form=fields)[0],400)
        finally:
            fixture.doCleanups()
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

    def test_packaged_java_class_keeps_package_and_private_field_test(self):
        source=b'package lecture.demo;\npublic class Point { private double positionX; }'
        test={'test_code':'java.lang.reflect.Field field = Point.class.getDeclaredField("positionX"); System.out.println(java.lang.reflect.Modifier.isPrivate(field.getModifiers()));'}
        generated,extra=templates.build(source,'java',{'answer_kind':'class'},test)
        self.assertEqual(extra,{'Point.java':source})
        self.assertTrue(generated.startswith(b'package lecture.demo;\npublic class Main'))
        self.assertIn(b'getDeclaredField("positionX")',generated)
        self.assertEqual(templates.java_package('// package fake.name;\npackage lecture.demo;\nclass Point {}'),'lecture.demo')

    def test_packaged_java_class_works_with_teacher_custom_template(self):
        source=b'package lecture.demo;\npublic class Point { private double positionX; }'
        template="import java.util.*;\n{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\npublic class __tester__ { public static void main(String[] args) throws Exception { {{ TEST.testcode }} } }"
        generated,_=templates.build(source,'java',{'answer_kind':'class','template':template},{'test_code':'System.out.println(Point.class.getDeclaredField("positionX").getType());'})
        self.assertTrue(generated.startswith(b'package lecture.demo;\nimport java.util.*;'))
        self.assertEqual(generated.count(b'package lecture.demo;'),1)
        self.assertIn(b'class Point {',generated)

    def test_packaged_java_runner_compiles_into_package_and_runs_qualified_main(self):
        from unittest.mock import patch
        commands=[]
        def container(folder,command,**kwargs):
            commands.append(command)
            return {'exit':0,'overflow':False,'system_error':False,'oom':False,'timed_out':False,
                    'stdout':'OK' if command[0]=='java' else '', 'stderr':'','time_ms':1}
        problem={'answer_kind':'class','points':10,'time_limit_ms':1000,'memory_limit_mb':256,
                 'checker':'tokens','tests':[{'input':'','output':'OK','sample':True,
                                            'test_code':'System.out.println("OK");'}]}
        source=b'package lecture.demo;\npublic class Point { private double positionX; }'
        with patch.object(code_runner,'ready',return_value=True),patch.object(code_runner,'_container',side_effect=container):
            result=code_runner.judge(source,'java',problem)
        self.assertEqual(result['verdict'],'AC')
        self.assertEqual(commands[0][-2:],['Main.java','Point.java'])
        self.assertIn('-d',commands[0])
        self.assertIn('Point.java',commands[0])
        self.assertEqual(commands[1][-1],'lecture.demo.Main')

    def test_packaged_complete_java_program_runs_its_own_main(self):
        from unittest.mock import patch
        commands=[]
        def container(folder,command,**kwargs):
            commands.append(command)
            return {'exit':0,'overflow':False,'system_error':False,'oom':False,'timed_out':False,
                    'stdout':'Point(0.0,0.0)' if command[0]=='java' else '', 'stderr':'','time_ms':1}
        problem={'answer_kind':'program','points':10,'time_limit_ms':1000,'memory_limit_mb':256,
                 'checker':'tokens','tests':[{'input':'','output':'Point(0.0,0.0)','sample':True}]}
        source=b'package lecture.demo; public class J05005 { public static void main(String[] args) { System.out.println("Point(0.0,0.0)"); } }'
        with patch.object(code_runner,'ready',return_value=True),patch.object(code_runner,'_container',side_effect=container):
            result=code_runner.judge(source,'java',problem)
        self.assertEqual(result['verdict'],'AC')
        self.assertIn('-d',commands[0])
        self.assertIn('J05005.java',commands[0])
        self.assertEqual(commands[1][-1],'lecture.demo.J05005')

    def test_visibility_is_independent_from_examples(self):
        self.assertFalse(templates.visible({'sample':True,'feedback_visibility':'hide'}))
        self.assertTrue(templates.visible({'sample':False,'feedback_visibility':'show'}))
        self.assertFalse(templates.visible({'verdict':'WA','feedback_visibility':'hide_if_fail'}))

    def test_missing_test_code_is_rejected(self):
        with self.assertRaises(ValueError):
            templates.validate({'answer_kind':'method','tests':[{}]})


@unittest.skipUnless(os.getenv('CSS_JUDGE_TESTS')=='1','Requires Docker')
class TemplateDockerTests(unittest.TestCase):
    def test_counter_demo_distinguishes_structure_from_matching_outputs(self):
        from scripts.seed_counter_attribute_demo import SOURCE, TESTS
        problem={'answer_kind':'class','points':100,'time_limit_ms':2000,'memory_limit_mb':256,
                 'checker':'exact','tests':TESTS}
        correct=code_runner.judge(SOURCE.encode(),'java',problem)
        exposed=SOURCE.replace('private int value;', 'public int value;')
        wrong=code_runner.judge(exposed.encode(),'java',problem)
        self.assertEqual((correct['verdict'],correct['score'],correct['passed']),('AC',100,5),correct)
        self.assertEqual((wrong['verdict'],wrong['score'],wrong['passed']),('WA',80,4),wrong)
        self.assertEqual([row['verdict'] for row in wrong['tests']],['WA','AC','AC','AC','AC'])

    def test_packaged_java_custom_template(self):
        template="import java.util.*;\n{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\npublic class __tester__ { public static void main(String[] args) throws Exception { {{ TEST.testcode }} } }"
        source='package lecture.demo;\npublic class Point { private double positionX; }'
        problem={'answer_kind':'class','template':template,'points':10,'checker':'exact',
                 'time_limit_ms':2000,'memory_limit_mb':256,
                 'tests':[{'input':'','output':'true','sample':True,
                           'test_code':'System.out.print(java.lang.reflect.Modifier.isPrivate(Point.class.getDeclaredField("positionX").getModifiers()));'}]}
        result=code_runner.judge(source.encode(),'java',problem)
        self.assertEqual(result['verdict'],'AC',result)

    def test_java_point_package_attributes_and_methods(self):
        from scripts.seed_point_class_example import TESTS
        source='''package lecture.demo;
public class Point {
    private double positionX = 0.0;
    private double positionY;
    public static String color;
    public Point() { this.positionX = 0.0; this.positionY = 0.0; }
    public Point(double x, double y) { this.positionX = x; this.positionY = y; }
    public double getPositionX() { return positionX; }
    public double getPositionY() { return positionY; }
    public void setPositionX(double x) { positionX = x; }
    public void setPositionY(double y) { positionY = y; }
    public static double getDistance(double x, double y, double x1, double y1) {
        return Math.sqrt(Math.pow(x1 - x, 2) + Math.pow(y1 - y, 2));
    }
    public void moveLeft(double speed) { positionX -= speed; }
    public void moveRight(double speed) { positionX += speed; }
    public void moveUp(double speed) { positionY += speed; }
    public void moveDown(double speed) { positionY -= speed; }
    public String toString() { return "Point(" + getPositionX() + "," + getPositionY() + ")"; }
}'''
        problem={'answer_kind':'class','points':100,'time_limit_ms':2000,'memory_limit_mb':256,
                 'checker':'exact','tests':TESTS}
        result=code_runner.judge(source.encode(),'java',problem)
        self.assertEqual(result['verdict'],'AC',result)
        self.assertEqual(result['passed'],len(TESTS))
        exposed=source.replace('private double positionX', 'public double positionX')
        invalid=code_runner.judge(exposed.encode(),'java',dict(problem,tests=TESTS[:1]))
        self.assertEqual(invalid['verdict'],'WA',invalid)

    def test_teacher_customised_product(self):
        from app import code_preview
        import json
        template="{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\npublic class __tester__ { public static void main(String[] args){ {{ TEST.testcode }} } }"
        problem={'answer_kind':'class','template':template,'language':'java','tests':[{'input':'','output':'7','test_code':'System.out.println(new Product().price());'}]}
        result=code_preview.run({'problem':json.dumps(problem),'source':'public class Product { public int price(){return 7;} }','language':'java'})
        self.assertEqual(result['verdict'],'AC',result)
    def run_case(self,language,kind,source,code,expected,verdict='AC'):
        problem={'answer_kind':kind,'points':10,'checker':'tokens','time_limit_ms':2000,'memory_limit_mb':256,'tests':[{'input':'','output':expected,'sample':True,'test_code':code}]}
        result=code_runner.judge(source.encode(),language,problem)
        self.assertEqual(result['verdict'],verdict,result)

    def test_java_class(self):
        self.run_case('java','class','public class Product { public int price(){return 7;} }','System.out.println(new Product().price());','7')

    def test_java_inheritance_in_one_source_file(self):
        source='abstract class Person { abstract String info(); } public class Student extends Person { String info(){return "ok";} }'
        self.run_case('java','class',source,'Person p = new Student(); System.out.println(p.info());','ok')

    def test_complete_java_program_with_named_entry_class(self):
        source='import java.util.*;\nclass Student { int value=7; }\npublic class J05005 { public static void main(String[] args){ System.out.println(new Student().value); } }'
        self.run_case('java','program',source,'','7')

    def test_named_entry_on_one_line_after_helper_and_comment(self):
        source='/* public class Fake {} */ import java.util.*; class Student { int value=7; } public class J05005 { public static void main(String[] args){ System.out.println(new Student().value); } }'
        self.run_case('java','program',source,'','7')

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
