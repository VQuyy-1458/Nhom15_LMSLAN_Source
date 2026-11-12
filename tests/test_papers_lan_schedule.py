"""Integration tests for shared questions, immutable papers, distribution and LAN attendance."""
import json
import time
import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from tests import test_learning as support
from app import storage,learning,exercise_bank,question_papers,programming,code_runner,lan_attendance

class IntegrationTests(unittest.TestCase):
    setUp=support.LearningTests.setUp
    cleanup=support.LearningTests.cleanup
    request=support.LearningTests.request
    create=support.LearningTests.create
    course=support.LearningTests.course

    def q(self,cid,name='Question',kind='code'):
        code,r=self.request('/api/admin/course-questions/save',form={'course_id':cid,'title':name,'purpose':'exam','response_type':kind,'statement':'Solve '+name,'languages':'python','problems':json.dumps([{'title':name,'tests':[{'input':'','output':'7','sample':False}]}])})
        self.assertEqual(code,200,r);return r['id']

    def paper(self,ids,kind='code',title='Paper'):
        code,r=self.request('/api/admin/question-papers/save',form={'title':title,'question_ids':json.dumps(ids),'response_type':kind})
        self.assertEqual(code,200,r);pid=r['id'];self.assertEqual(self.request('/api/admin/question-papers/publish',form={'id':pid})[0],200);return pid

    def test_shared_question_can_be_enabled_for_practice_and_used_in_multiple_courses(self):
        a=self.course('s1 s2');b=self.create('course',name='Other',code='B',semester='2026',student_ids='s1')
        qid=self.q(a);row=exercise_bank.bank()[0]
        form={**row,'course_ids':json.dumps([a,b]),'languages':'python','problems':json.dumps(row['programming']['problems'])}
        self.assertEqual(self.request('/api/admin/course-questions/save',form=form)[0],200)
        self.assertEqual(self.request('/api/admin/course-questions/publish',form={'id':qid})[0],200)
        self.assertEqual(len(exercise_bank.bank()),1)
        self.assertEqual(len([r for r in exercise_bank.code_rows() if r.get('practice')]),2)
        self.assertEqual(self.request('/api/admin/question-papers/save','s1',{})[0],403)
        pid=self.paper([qid]);code,r=self.request('/api/admin/course-practicals/save',form={'course_id':b,'title':'Other course sitting','paper_ids':json.dumps([pid]),'response_type':'code','duration_minutes':'40'})
        self.assertEqual(code,200,r)

    def test_link_unlink_is_course_scoped_even_for_last_course(self):
        a=self.course('s1 s2');b=self.create('course',name='Other',code='B',semester='2026',student_ids='s1')
        qid=self.q(a);self.assertEqual(self.request('/api/admin/course-questions/publish',form={'id':qid})[0],200)
        def link(cid,enabled,role='admin'):
            return self.request('/api/admin/course-questions/link',role,{'id':qid,'target_course_id':cid,'enabled':str(enabled).lower()})[0]
        def courses():return {r['course_id'] for r in exercise_bank.code_rows() if r.get('practice')}
        self.assertEqual(courses(),{a});self.assertEqual(link(b,True,'s1'),403)
        self.assertEqual(link(b,True),200);self.assertEqual(courses(),{a,b})
        self.assertEqual(link(a,False),200);self.assertEqual(courses(),{b})
        self.assertEqual(link(b,False),200);self.assertEqual(courses(),set())
        self.assertEqual(link(a,True),200);self.assertEqual(courses(),{a})

    def test_paper_snapshot_and_random_question_access_and_scores(self):
        cid=self.course('s1 s2');ids=[self.q(cid,'Q'+str(i)) for i in range(3)];pid=self.paper(ids)
        self.assertEqual(self.request('/api/admin/question-papers/save',form={'id':pid,'title':'Changed'})[0],409)
        code,r=self.request('/api/admin/exam-configurations/save',form={'course_id':cid,'title':'Random midterm','type':'programming','assessment_type':'midterm','paper_ids':json.dumps([pid]),'paper_distribution':'random_questions','questions_per_student':'1'})
        self.assertEqual(code,200,r);eid=r['id']
        # Changing the bank cannot change the published paper or an existing exam.
        rows=exercise_bank.bank();rows[0]['programming']['problems'][0]['title']='Modified later';storage.write_json(exercise_bank.BANK,rows)
        self.assertEqual(programming.exam(eid)['programming']['problems'][0]['title'],'Q0')
        with patch.object(code_runner,'ready',return_value=True):self.assertEqual(self.request('/api/admin/programming/control',form={'exam_id':eid,'action':'start'})[0],200)
        row=programming.exam(eid);sets=row['student_problem_sets'];self.assertNotEqual(sets['s1'],sets['s2'])
        with patch.object(code_runner,'ready',return_value=True),patch.object(programming,'schedule'):
            for sid in ['s1','s2']:
                self.assertEqual(self.request('/api/student/programming/start',sid,{'exam_id':eid})[0],200)
                assigned=sets[sid][0];forbidden=next(i for i in range(3) if i not in sets[sid])
                self.assertEqual(self.request('/api/student/programming/submissions?exam='+eid+'&problem='+str(forbidden),sid)[0],403)
                self.assertEqual(self.request('/api/student/programming/submit',sid,{'exam_id':eid,'problem_index':str(forbidden),'language':'python'},file=('main.py',b'print(7)'))[0],403)
                code,result=self.request('/api/student/programming/submit',sid,{'exam_id':eid,'problem_index':str(assigned),'language':'python'},file=('main.py',b'print(7)'));self.assertEqual(code,200,result)
                with patch.object(code_runner,'judge',return_value={'verdict':'AC','score':100,'tests':[],'compile_log':''}):programming._work(result['submission']['id'])
                own=self.request('/api/student/workspace',sid)[1];exam=next(e for e in own['programming']['exams'] if e['id']==eid)
                self.assertEqual([p['index'] for p in exam['problems']],sets[sid]);self.assertNotIn('student_problem_sets',json.dumps(own))
                self.assertEqual(own['gradebooks'][0]['items'][0]['midterm'],10)
        self.assertEqual(programming.exam(eid)['student_problem_sets'],sets)

    def test_random_papers_remain_stable_and_file_papers_use_native_file_engine(self):
        cid=self.course('s1 s2');pids=[self.paper([self.q(cid,'Code'+str(i))],title='Variant '+str(i)) for i in range(2)]
        code,r=self.request('/api/admin/course-practicals/save',form={'course_id':cid,'title':'Variants','paper_ids':json.dumps(pids),'paper_distribution':'random_papers','response_type':'code'});self.assertEqual(code,200,r)
        with patch.object(code_runner,'ready',return_value=True):self.assertEqual(self.request('/api/admin/course-practicals/start',form={'id':r['id']})[0],200)
        row=programming.exam(r['id']);self.assertNotEqual(row['student_papers']['s1'],row['student_papers']['s2'])
        fids=[self.paper([self.q(cid,'Report'+str(i),'file')],kind='file',title='Report variant '+str(i)) for i in range(2)]
        from app import exams
        from pathlib import Path
        folder=Path(self.temp.name)/'bank-exams';folder.mkdir()
        with patch.object(exams,'EXAM_DIR',folder),patch('app.config.EXAM_DIR',folder):
            code,r=self.request('/api/admin/exam-configurations/save',form={'type':'file','course_id':cid,'title':'Reports','paper_ids':json.dumps(fids),'paper_distribution':'random_papers'})
            self.assertEqual(code,200,r);eid=r['id'];self.assertEqual(self.request('/api/admin/exam-configurations/activate',form={'id':eid})[0],200)
            with storage.atomic_transaction():result=exams.distribute_exams('random')
            assignments=storage.read_json('assignments.json');self.assertNotEqual(assignments['s1']['exam_file'],assignments['s2']['exam_file'])
            self.assertTrue((folder/assignments['s1']['exam_file']).is_file())

    def test_bulk_schedule_crosses_year_skips_duplicates_and_rejects_invalid_without_writes(self):
        cid=self.course();f={'course_id':cid,'title':'Networking','start_week':'2026-W52','end_week':'2027-W02','weekday':'2','start_time':'07:30','end_time':'10:00','location':'Lab'}
        code,r=self.request('/api/admin/schedule/bulk',form=f);self.assertEqual(code,200,r);self.assertEqual(r['created'],4)
        rows=learning.load()['events'];self.assertTrue(all(e.get('ends_at') for e in rows))
        code,r=self.request('/api/admin/schedule/bulk',form=f);self.assertEqual(code,200,r);self.assertEqual(r['created'],0);self.assertEqual(r['skipped'],4)
        self.assertEqual(self.request('/api/admin/schedule/bulk',form={**f,'end_time':'06:00'})[0],400);self.assertEqual(len(learning.load()['events']),4)
        self.assertEqual(self.request('/api/admin/schedule/bulk','s1',f)[0],403)

    def test_lan_attendance_only_recent_real_sessions_manual_overrides_and_after_close(self):
        cid=self.course('s1 s2');tokens=storage.read_json('sessions.json')
        for row in tokens.values():
            if row['user_id']=='s2':row['last_seen']=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
        storage.write_json('sessions.json',tokens)
        eid=self.create('event',course_id=cid,title='Lab',kind='lesson',starts_at=storage.utc_now())
        aid=self.create('attendance',course_id=cid,event_id=eid,title='Lab',mode='lan',duration_minutes='10')
        row=learning.load()['attendance'][0];self.assertIn('s1',row['records']);self.assertNotIn('s2',row['records'])
        self.request('/api/student/workspace','s2');row=learning.load()['attendance'][0];self.assertIn('s2',row['records'])
        self.assertEqual(self.request('/api/learning/close-attendance',form={'session_id':aid})[0],200)
        self.assertEqual(self.request('/api/learning/attendance-record',form={'session_id':aid,'student_id':'s1','status':'early_departure'})[0],200)
        self.request('/api/student/workspace','s1');self.assertEqual(learning.load()['attendance'][0]['records']['s1']['status'],'early_departure')
        self.assertFalse(lan_attendance.lan_ip('8.8.8.8'));self.assertTrue(lan_attendance.lan_ip('192.168.1.5'))
        self.assertEqual(self.request('/api/learning/attendance-record','s1',{'session_id':aid,'student_id':'s1','status':'present'})[0],403)

if __name__=='__main__':unittest.main()
