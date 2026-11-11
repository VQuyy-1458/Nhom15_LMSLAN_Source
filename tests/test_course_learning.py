"""End-to-end access, snapshots, common practical clock, grades and weekly links."""
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from tests import test_learning as support
from app import storage, learning, programming, exercise_bank, code_runner


class CourseLearningTests(unittest.TestCase):
    setUp=support.LearningTests.setUp
    cleanup=support.LearningTests.cleanup
    request=support.LearningTests.request
    create=support.LearningTests.create
    course=support.LearningTests.course

    def question(self,course,purpose='practice',kind='code',title='Visible practice',**extra):
        fields={'course_id':course,'title':title,'purpose':purpose,'response_type':kind,'statement':'Requirement '+title,
            'languages':'python','week_number':'2','problems':json.dumps([{'title':title,'tests':[{'input':'1 2','output':'3','sample':True},{'input':'SECRET-HIDDEN','output':'3','sample':False}]}]),**extra}
        code,result=self.request('/api/admin/course-questions/save',form=fields)
        self.assertEqual(code,200,result);return result['id']

    def publish(self,qid):
        self.assertEqual(self.request('/api/admin/course-questions/publish',form={'id':qid})[0],200)

    def practical(self,course,qids,kind='code'):
        code,result=self.request('/api/admin/course-practicals/save',form={'course_id':course,'title':'Practical session','response_type':kind,'question_ids':json.dumps(qids),'duration_minutes':'60','student_ids':'s1','week_number':'2'})
        self.assertEqual(code,200,result);return result['id']

    def test_practice_private_purposes_enrollment_and_unpublish(self):
        course=self.course();qid=self.question(course);private=self.question(course,'practical',title='PRIVATE PRACTICAL');exam=self.question(course,'exam',title='PRIVATE EXAM')
        own=lambda:self.request('/api/student/workspace','s1')[1]
        self.assertNotIn('Visible practice',json.dumps(own()))
        for private_id in [private,exam]:
            self.assertEqual(self.request('/api/admin/course-questions/publish',form={'id':private_id})[0],200)
            self.assertEqual(self.request('/api/admin/course-questions/unpublish',form={'id':private_id})[0],200)
        self.publish(qid);public=own();self.assertIn('Visible practice',json.dumps(public));self.assertNotIn('PRIVATE',json.dumps(public));self.assertNotIn('SECRET-HIDDEN',json.dumps(public));self.assertNotIn('question_bank',public)
        pid=exercise_bank.practice_id(next(q for q in exercise_bank.bank() if q['id']==qid),course)
        self.assertEqual(self.request('/api/student/programming/start','s2',{'exam_id':pid})[0],403)
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':pid})[0],200)
        self.assertNotIn('SECRET-HIDDEN',json.dumps(own()))
        self.assertEqual(self.request('/api/admin/course-questions/save','s1',{})[0],403)
        self.assertEqual(self.request('/api/admin/course-questions/unpublish',form={'id':qid})[0],200)
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':pid})[0],404)
        self.assertFalse(own()['programming']['exams'])

    def test_practical_snapshot_common_deadline_and_code_grade(self):
        course=self.course();qid=self.question(course,'practical',title='Secret practical');sid=self.practical(course,[qid]);self.assertNotIn('Secret practical',json.dumps(self.request('/api/student/workspace','s1')[1]))
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':sid})[0],409)
        with patch.object(code_runner,'ready',return_value=True):self.assertEqual(self.request('/api/admin/course-practicals/start',form={'id':sid})[0],200)
        ends=programming.exam(sid)['ends_at']
        self.assertEqual(self.request('/api/student/programming/start','s2',{'exam_id':sid})[0],403)
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':sid})[0],200)
        self.assertEqual(storage.read_json('programming_attempts.json')[sid+':s1']['ends_at'],ends)
        # Editing a bank question must not mutate the already assigned snapshot.
        self.question(course,'practical',title='Replacement')
        self.assertEqual(programming.exam(sid)['programming']['problems'][0]['title'],'Secret practical')
        with patch.object(code_runner,'ready',return_value=True),patch.object(programming,'schedule'):
            code,result=self.request('/api/student/programming/submit','s1',{'exam_id':sid,'problem_index':'0','language':'python'},file=('answer.py',b'print(3)'))
        self.assertEqual(code,200,result)
        with patch.object(code_runner,'judge',return_value={'verdict':'AC','score':100,'passed':2,'total':2,'tests':[],'compile_log':''}):programming._work(result['submission']['id'])
        workspace=self.request('/api/student/workspace','s1')[1]
        self.assertEqual(workspace['gradebooks'][0]['items'][0]['homework'],10)
        self.assertEqual(programming.rows()[0]['activity_type'],'practical')
        self.assertTrue((programming.FILES/result['submission']['id']/'source').is_file())
        self.assertEqual(self.request('/api/admin/course-practicals/end',form={'id':sid})[0],200)
        with patch.object(code_runner,'ready',return_value=True):self.assertEqual(self.request('/api/student/programming/submit','s1',{'exam_id':sid,'problem_index':'0','language':'python'},file=('answer.py',b'print(3)'))[0],409)

    def test_file_practice_and_practical_access_and_grade_exclusion(self):
        course=self.course();qid=self.question(course,kind='file');self.publish(qid);aid=exercise_bank.practice_id(next(q for q in exercise_bank.bank() if q['id']==qid),course)
        self.assertEqual(self.request('/api/learning/submit','s2',{'assignment_id':aid,'request_id':'x'},file=('answer.txt',b'ok'))[0],403)
        code,result=self.request('/api/learning/submit','s1',{'assignment_id':aid,'request_id':'x'},file=('answer.txt',b'ok'));self.assertEqual(code,200,result)
        self.create('grade',submission_id=result['id'],score='9')
        self.assertIsNone(self.request('/api/student/workspace','s1')[1]['gradebooks'][0]['items'][0]['homework'])
        self.assertEqual(self.request('/api/admin/course-questions/unpublish',form={'id':qid})[0],200)
        self.assertEqual(self.request('/api/learning/submit','s1',{'assignment_id':aid,'request_id':'new'},file=('answer.txt',b'ok'))[0],403)
        qid=self.question(course,'practical','file','Private report');pid=self.practical(course,[qid],'file')
        self.assertEqual(self.request('/api/admin/course-practicals/start',form={'id':pid})[0],200)
        aid=pid+'_0'
        self.assertNotIn('Private report',json.dumps(self.request('/api/student/workspace','s2')[1]))
        self.assertEqual(self.request('/api/learning/submit','s2',{'assignment_id':aid,'request_id':'bad'},file=('answer.txt',b'ok'))[0],403)
        self.assertEqual(self.request('/api/learning/submit','s1',{'assignment_id':aid,'request_id':'ok'},file=('answer.py',b'ok'))[0],400)
        self.assertEqual(self.request('/api/learning/submit','s1',{'assignment_id':aid,'request_id':'ok'},file=('answer.txt',b'ok'))[0],200)

    def test_weekly_references_are_course_scoped_and_private_ids_are_hidden(self):
        c1=self.course();c2=self.create('course',name='Other',code='OTHER',semester='2026',student_ids='s2')
        m=self.request('/api/learning/material',form={'course_id':c1,'title':'Material','week_number':'2'},file=('notes.txt',b'notes'))[1]['id']
        q=self.question(c1,'practical');activity=self.practical(c1,[q])
        form={'course_id':c1,'week_number':'2','title':'TCP week','lesson_text':'Lecture','reading_text':'Read chapter 2','material_ids':json.dumps([m]),'activity_ids':json.dumps([activity])}
        self.assertEqual(self.request('/api/admin/course-content/save',form=form)[0],200)
        student=self.request('/api/student/workspace','s1')[1];self.assertEqual(student['course_weeks'][0]['material_ids'],[m]);self.assertEqual(student['course_weeks'][0]['activity_ids'],[])
        self.assertEqual(self.request('/api/admin/course-content/save','s1',form)[0],403)
        self.assertEqual(self.request('/api/admin/course-content/save',form={**form,'course_id':c2})[0],400)
        self.assertFalse(self.request('/api/student/workspace','s2')[1]['course_weeks'])
        self.assertEqual(student['materials'][0]['week_number'],2)

    def test_customise_survives_bank_and_practical_snapshot(self):
        course=self.course()
        spec={'title':'Product','answer_kind':'class','language':'java','template':'{{ STUDENT_ANSWER }}\npublic class Main { public static void main(String[] args){ {{ TEST.testcode }} } }','tests':[{'input':'','output':'7','test_code':'System.out.println(new Product().price());','sample':True}]}
        qid=self.question(course,'practical',languages='java',problems=json.dumps([spec]))
        pid=self.practical(course,[qid]);saved=programming.exam(pid)['programming']['problems'][0]
        self.assertEqual(saved['template'],spec['template']);self.assertEqual(saved['tests'][0]['test_code'],spec['tests'][0]['test_code'])

    def test_unassigned_file_work_does_not_reduce_another_students_grade(self):
        course=self.course('s1 s2');qid=self.question(course,'practical','file','Selected report');pid=self.practical(course,[qid],'file')
        self.assertEqual(self.request('/api/admin/course-practicals/start',form={'id':pid})[0],200)
        self.assertEqual(self.request('/api/admin/course-practicals/end',form={'id':pid})[0],200)
        own=self.request('/api/student/workspace','s2')[1]
        self.assertEqual(own['assignments'],[])
        self.assertIsNone(own['gradebooks'][0]['items'][0]['homework'])

    def test_sample_run_is_private_unstored_and_completed_course_closes_poll(self):
        course=self.course();qid=self.question(course);self.publish(qid);eid=exercise_bank.practice_id(next(q for q in exercise_bank.bank() if q['id']==qid),course)
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':eid})[0],200)
        form={'exam_id':eid,'problem_index':'0','language':'python','source':'print(3)'}
        result={'verdict':'AC','score':100,'private_compile_log':'secret','tests':[{'sample':True,'actual':'3'}]}
        with patch.object(code_runner,'ready',return_value=True),patch.object(code_runner,'judge',return_value=result) as judge:
            code,result=self.request('/api/student/programming/run','s1',form)
            self.assertEqual(code,200,result);self.assertNotIn('score',result['result']);self.assertNotIn('private_compile_log',result['result']);self.assertEqual(len(judge.call_args.args[2]['tests']),1)
        self.assertEqual(programming.rows(),[])
        data=learning.load();data['courses'][0]['status']='completed';storage.write_json('learning.json',data)
        self.assertEqual(self.request('/api/student/programming/run','s1',form)[0],404)

    def test_java_type_detection_ignores_nested_types_and_literals(self):
        self.assertEqual(code_runner.java_public_class(b'// public class Decoy {}\nclass Helper { public class Nested {} } public final class J05005 { String s="public class StringFake {}"; }'),'J05005')
        self.assertEqual(code_runner.java_public_class(b'import java.util.*; public class Real {}'),'Real')


if __name__=='__main__':unittest.main()
