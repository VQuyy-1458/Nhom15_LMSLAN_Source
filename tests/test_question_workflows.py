"""Integration coverage for practice, papers and per-student programming sets."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_learning as support
from app import storage, programming, code_runner, learning, exams, main, question_library


class QuestionWorkflowTests(unittest.TestCase):
    def test_customise_survives_library_and_teacher_can_preview(self):
        course,other,fields=self.teacher_context()
        template="{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\npublic class __tester__ { public static void main(String[] args){ {{ TEST.testcode }} } }"
        spec={'title':'Product','answer_kind':'class','template':template,'language':'java','tests':[{'input':'','output':'7','sample':True,'test_code':'System.out.println(new Product().price());','feedback_visibility':'hide'}]}
        fields={**fields,'languages':'java','problems':json.dumps([spec])}
        qid=self.question(fields,'practice')
        self.assertEqual(self.request('/api/admin/questions/publish','t1',{'id':qid})[0],200)
        q=question_library.practice_rows('s1')[0]
        self.assertEqual(q['programming']['problems'][0]['template'],template)
        self.assertEqual(q['programming']['problems'][0]['tests'][0]['test_code'],spec['tests'][0]['test_code'])
        with patch.object(code_runner,'judge',return_value={'verdict':'AC','tests':[]}):
            status,result=self.request('/api/admin/programming/preview','t1',{'language':'java','source':'public class Product {}','problem':json.dumps(spec)})
        self.assertEqual(status,200,result)

    setUp = support.LearningTests.setUp
    cleanup = support.LearningTests.cleanup
    request = support.LearningTests.request
    create = support.LearningTests.create
    course = support.LearningTests.course
    teacher_context = support.LearningTests.teacher_context

    def question(self, fields, purpose="exam", title="Library problem"):
        problems=json.loads(fields['problems']);problems[0]['title']=title
        problems[0]['statement']='Private statement '+title
        form={**fields,'purpose':purpose,'problems':json.dumps(problems)}
        code,result=self.request('/api/admin/questions/save','t1',form)
        self.assertEqual(code,200,result)
        return storage.read_json('questions.json')[-1]['id']

    def file_question(self, course, purpose="exam"):
        form={'course_id':course,'purpose':purpose,'response_type':'file','file_title':'Report',
              'file_statement':'Explain the TCP handshake and submit a PDF report.', 'file_extensions':'.pdf .txt'}
        code,result=self.request('/api/admin/questions/save','t1',form)
        self.assertEqual(code,200,result)
        return storage.read_json('questions.json')[-1]['id']

    def test_published_practice_is_enrollment_scoped_and_not_a_course_mark(self):
        course,other,fields=self.teacher_context()
        data=learning.load();next(c for c in data['courses'] if c['id']==course)['student_ids']=['s1'];storage.write_json('learning.json',data)
        qid=self.question(fields,'practice')
        self.question(fields,'practical','Secret practical')
        self.assertFalse(question_library.practice_rows('s1'))
        self.assertEqual(self.request('/api/admin/questions/publish','t1',{'id':qid})[0],200)
        own=question_library.practice_rows('s1');self.assertEqual(len(own),1)
        self.assertFalse(question_library.practice_rows('s2'))
        self.assertEqual(self.request('/api/student/programming/start','s2',{'exam_id':own[0]['id']})[0],403)
        self.assertEqual(self.request('/api/student/programming/start','s1',{'exam_id':own[0]['id']})[0],200)
        workspace=self.request('/api/student/workspace','s1')[1]
        self.assertEqual(len([e for e in workspace['programming']['exams'] if e.get('practice')]),1)
        self.assertNotIn('Secret practical',json.dumps(workspace))
        fid=self.file_question(course,'practice')
        self.assertEqual(self.request('/api/admin/questions/publish','t1',{'id':fid})[0],200)
        task='practice_'+fid
        self.assertEqual(self.request('/api/learning/submit','s1',{'assignment_id':task,'request_id':'practice-file'},file=('answer.py',b'print(3)'))[0],400)
        code,result=self.request('/api/learning/submit','s1',{'assignment_id':task,'request_id':'practice-file'},file=('answer.txt',b'TCP report'))
        self.assertEqual(code,200,result)
        self.assertEqual(self.request('/api/learning/grade','t1',{'submission_id':result['id'],'score':'10','feedback':'Good'})[0],200)
        book=learning.gradebook(learning.load(),next(c for c in learning.load()['courses'] if c['id']==course),['s1'])
        self.assertIsNone(book['items'][0]['homework'])
        self.assertEqual(self.request('/api/admin/questions/archive','t1',{'id':fid})[0],200)
        self.assertEqual(self.request('/api/learning/submit','s1',{'assignment_id':task,'request_id':'after-archive'},file=('answer.txt',b'Again'))[0],403)

    def test_paper_snapshot_is_reusable_and_owner_protected(self):
        course,other,fields=self.teacher_context()
        qid=self.question(fields)
        form={'course_id':course,'title':'Independent paper','response_type':'code','question_ids':json.dumps([qid])}
        code,result=self.request('/api/admin/papers/save','t1',form)
        self.assertEqual(code,200,result);pid=result['id']
        self.assertEqual(self.request('/api/admin/papers/publish','t2',{'id':pid})[0],403)
        self.assertEqual(self.request('/api/admin/papers/publish','s1',{'id':pid})[0],403)
        self.assertEqual(self.request('/api/admin/papers/publish','t1',{'id':pid})[0],200)
        self.assertEqual(self.request('/api/admin/papers/save','t1',{**form,'id':pid})[0],409)
        self.assertEqual(self.request('/api/admin/questions/save','t1',{**fields,'id':qid,'problems':fields['problems']})[0],200)
        saved=storage.read_json('exam_blueprints.json')[0]
        self.assertEqual(saved['programming']['problems'][0]['title'],'Library problem')
        ids=[]
        for name in ['First sitting','Second sitting']:
            code,result=self.request('/api/admin/exam-configurations/save','t1',{'course_id':course,'type':'programming','title':name,'blueprint_id':pid,'distribution_mode':'manual'})
            self.assertEqual(code,200,result);ids.append(result['id'])
        self.assertNotEqual(*ids)
        self.assertEqual(programming.exam(ids[0])['programming']['problems'][0]['title'],'Library problem')
        self.assertEqual(self.request('/api/admin/papers/archive','t1',{'id':pid})[0],200)
        self.assertEqual(self.request('/api/admin/exam-configurations/save','t1',{'course_id':course,'type':'programming','title':'Blocked','blueprint_id':pid})[0],409)
        self.assertEqual(programming.exam(ids[0])['programming']['problems'][0]['title'],'Library problem')

    def test_random_code_sets_are_stable_private_and_scored_per_student(self):
        course,other,fields=self.teacher_context()
        ids=[self.question(fields,title='Question '+str(i)) for i in range(3)]
        form={**fields,'type':'programming','assessment_type':'midterm','distribution_mode':'manual',
              'question_ids':json.dumps(ids),'problems':'[]','paper_distribution':'random','questions_per_student':'1'}
        code,result=self.request('/api/admin/exam-configurations/save','t1',form)
        self.assertEqual(code,200,result);eid=result['id']
        with patch('app.question_library.random.SystemRandom') as rng:
            rng.return_value.sample.side_effect=[[0],[1]]
            self.assertEqual(self.request('/api/admin/programming/control','t1',{'exam_id':eid,'action':'publish'})[0],200)
        fixed=copy.deepcopy(programming.exam(eid)['student_problem_sets'])
        self.assertEqual(fixed,{'s1':[0],'s2':[1]})
        with patch.object(code_runner,'ready',return_value=True),patch.object(programming,'schedule'):
            self.assertEqual(self.request('/api/admin/programming/control','t1',{'exam_id':eid,'action':'start'})[0],200)
            for sid,index in [('s1',0),('s2',1)]:
                self.assertEqual(self.request('/api/student/programming/start',sid,{'exam_id':eid})[0],200)
                own=next(e for e in programming.snapshot(sid)['exams'] if e['id']==eid)
                self.assertEqual([p['index'] for p in own['problems']],[index])
                self.assertEqual(self.request('/api/student/programming/submissions?exam='+eid+'&problem=2',sid)[0],403)
                self.assertEqual(self.request('/api/student/programming/submit',sid,{'exam_id':eid,'problem_index':'2','language':'python'},file=('main.py',b'print(3)'))[0],403)
                code,result=self.request('/api/student/programming/submit',sid,{'exam_id':eid,'problem_index':str(index),'language':'python'},file=('main.py',b'print(3)'))
                self.assertEqual(code,200,result)
                with patch.object(code_runner,'judge',return_value={'verdict':'AC','score':100,'passed':1,'total':1,'tests':[],'compile_log':''}):programming._work(result['submission']['id'])
            summary=programming.results({'role':'teacher','user_id':'t1'},eid)
            self.assertEqual([r['score_10'] for r in summary['results']],[10,10])
            self.assertEqual(summary['results'][0]['problem_scores'],[100,None,None])
        self.assertEqual(programming.exam(eid)['student_problem_sets'],fixed)
        from app.course_grades import exam_marks
        self.assertEqual(exam_marks(course,['s1','s2'])['s1'][0]['score'],10)
        self.assertNotIn('student_problem_sets',json.dumps(programming.snapshot('s1')))

    def test_file_bank_questions_can_be_assigned_and_used_in_teacher_exam(self):
        course,other,fields=self.teacher_context()
        qid=self.file_question(course,'practical')
        assignment={'course_id':course,'title':'Practical report','due_at':self.future,'question_ids':json.dumps([qid])}
        self.assertEqual(self.request('/api/admin/questions/assign-files','t2',assignment)[0],403)
        code,result=self.request('/api/admin/questions/assign-files','t1',assignment)
        self.assertEqual(code,200,result)
        self.assertIn('TCP',next(a for a in learning.load()['assignments'] if a['id']==result['id'])['description'])
        code,result=self.request('/api/admin/papers/save','t1',{'course_id':course,'title':'File paper','response_type':'file','question_ids':json.dumps([qid])})
        self.assertEqual(code,200,result);pid=result['id']
        self.assertEqual(self.request('/api/admin/papers/publish','t1',{'id':pid})[0],200)
        with patch.object(exams,'EXAM_DIR',Path(self.temp.name)/'exam-bank-files'):
            code,result=self.request('/api/admin/exam-configurations/save','t1',{'type':'file','course_id':course,'title':'File sitting','blueprint_id':pid})
            self.assertEqual(code,200,result);eid=result['id']
            self.assertEqual(self.request('/api/admin/papers/file-control','t2',{'exam_id':eid,'action':'distribute'})[0],403)
            code,result=self.request('/api/admin/papers/file-control','t1',{'exam_id':eid,'action':'distribute','student_ids':'s1'})
            self.assertEqual(code,200,result)
            self.assertEqual(set(storage.read_json('assignments.json')),{'s1'})
            self.assertEqual(self.request('/api/admin/papers/file-control','t1',{'exam_id':eid,'action':'start'})[0],200)
            self.assertEqual(storage.read_json('settings.json')['exam_state'],'started')
            self.assertEqual(self.request('/api/admin/papers/file-control','t1',{'exam_id':eid,'action':'end'})[0],200)
            self.assertEqual(storage.read_json('settings.json')['exam_state'],'ended')


if __name__ == '__main__':unittest.main()
