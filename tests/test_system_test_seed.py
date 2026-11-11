"""Verify sample-data integrity, repeat safety and usable test workflows."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]


class SystemTestSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="lms-full-fixture-")
        cls.root = Path(cls.temp.name) / "fixture"
        cls.env = {**os.environ, "PYTHONUTF8": "1", "CSS_DATA_ROOT": str(cls.root)}
        cls.run_seed()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def run_seed(cls, *args):
        result = subprocess.run([sys.executable, "-m", "scripts.seed_system_test", "--root", str(cls.root), *args],
                                cwd=PROJECT, env=cls.env, capture_output=True, text=True, encoding="utf-8", timeout=60)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(result.stdout)

    def documents(self):
        with closing(sqlite3.connect(self.root / "data" / "lms.sqlite3")) as db:
            return {name: json.loads(payload) for name, payload in db.execute("SELECT name,payload FROM documents")}

    def run_code(self, code):
        result = subprocess.run([sys.executable, "-c", code], cwd=PROJECT, env=self.env,
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repeat_preserves_records_and_password_hashes(self):
        self.run_code("""
from app import storage, security
students=storage.read_json('students.json')
students['TESTLONG']['password_hash']=security.hash_password('changed-by-test')
storage.write_json('students.json',students)
""")
        before = self.documents()
        self.run_seed()
        self.assertEqual(before, self.documents())
        self.assertEqual(self.run_seed("--check")["archive"]["missing"], 0)

    def test_coverage_and_private_test_snapshots(self):
        docs = self.documents()
        self.assertEqual(len(docs["students.json"]), 51)
        self.assertGreaterEqual(len(docs["learning.json"]["assignments"]), 47)
        self.assertEqual({r["result"]["verdict"] for r in docs["programming_submissions.json"]},
                         {"AC", "WA", "CE", "TLE", "MLE", "RE", "SYSTEM_ERROR"})
        self.assertTrue(all(r["fixture"] for r in docs["programming_submissions.json"]))
        self.run_code("""
from app import programming, learning, storage, security
assert not learning.snapshot({'role':'student','user_id':'TESTEMPTY'})['courses']
snapshot=programming.snapshot('DEMO001')
assert any(e['can_start'] for e in snapshot['exams'] if e['activity_type']=='exam')
for exam in snapshot['exams']:
    if not exam['attempt']: assert not exam['problems']
assert not storage.read_json('students.json')['TESTLOCKED']['active']
assert not security.login_allowed('testthrottle')[0]
""")

    def test_sample_imports_limits_and_authorization(self):
        self.run_code("""
import json
from pathlib import Path
from app import config, accounts, learning, course_packages, storage
root=config.RUNTIME_DIR
rows,errors=accounts.parse_accounts((root/'test-inputs/import-tai-khoan.txt').read_text(encoding='utf-8'))
assert len(rows)==2 and not errors
rows,errors=accounts.parse_accounts((root/'test-inputs/import-tai-khoan-loi.txt').read_text(encoding='utf-8'))
assert len(rows)==1 and len(errors)==3
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
task=manifest['limit_assignment']
assert len([s for s in learning.load()['submissions'] if s['assignment_id']==task and s['student_id']=='DEMO004'])==3
try:
    learning.mutate({'role':'student','user_id':'DEMO004'},'submit',{'assignment_id':task,'request_id':'test-fourth-attempt'},
                    {'file':{'filename':'extra.pdf','data':(root/'test-inputs/bao-cao.pdf').read_bytes()}},'127.0.0.1')
except learning.LearningError as e: assert e.status==409
else: raise AssertionError('Submission limit not enforced')
before=len(learning.load()['courses'])
file={'filename':'course.json','data':(root/'test-inputs/khoa-hoc-import.json').read_bytes()}
try: course_packages.import_course(file,{'role':'student','user_id':'DEMO001'},'127.0.0.1')
except learning.LearningError as e: assert e.status==403
else: raise AssertionError('Student imported an admin package')
course_packages.import_course(file,{'role':'admin','user_id':'testadmin'},'127.0.0.1')
assert len(learning.load()['courses'])==before+1
""")

    def test_refuses_normal_runtime_directory(self):
        result = subprocess.run([sys.executable, "-m", "scripts.seed_system_test", "--root", str(PROJECT)],
                                cwd=PROJECT, env=self.env, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("isolated", result.stderr)

    def test_real_http_login_and_role_permissions(self):
        self.run_code("""
import http.cookiejar, threading, urllib.request, urllib.parse, urllib.error, json
from app import main
main.Handler.log_message=lambda *args: None
server=main.ThreadingHTTPServer(('127.0.0.1',0),main.Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base='http://127.0.0.1:'+str(server.server_port)
try:
    for username,path in [('testadmin','/api/admin/workspace'),('DEMO001','/api/student/workspace'),('TESTEMPTY','/api/student/workspace')]:
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with opener.open(base+'/login',urllib.parse.urlencode({'username':username,'password':'111111'}).encode(),timeout=5) as response:
            assert response.status==200
        with opener.open(base+path,timeout=5) as response: data=json.load(response)
        if username=='TESTEMPTY': assert not data['courses']
        else: assert data['courses']
        if username!='testadmin':
            try: opener.open(base+'/api/admin/workspace',timeout=5)
            except urllib.error.HTTPError as error: assert error.code==403
            else: raise AssertionError('Student accessed admin workspace')
finally:
    server.shutdown();server.server_close();thread.join(timeout=3)
""")


if __name__ == "__main__":
    unittest.main()
