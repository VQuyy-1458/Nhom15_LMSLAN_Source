"""Add Docker judge examples to the current SQLite-backed course bank, idempotently."""
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import exercise_bank,code_templates,learning
from app.storage import read_json,write_json,atomic_transaction,utc_now,audit


def samples():
    return [
        ('cpp_program','[Docker mẫu] C++ program - Tổng hai số','cpp','program',
         'Nộp chương trình C++ hoàn chỉnh có main. Đọc đủ hai số nguyên a, b, |a|, |b| <= 10^9; in a+b.',
         [('1 2\n','3\n',''),('-5 8\n','3\n',''),('1000000000 1000000000\n','2000000000\n','')]),
        ('java_class','[Docker mẫu] Java class - Product','java','class',
         'Nộp public class Product với constructor public Product(int price, int quantity) và phương thức public long total(). total trả price*quantity. Không viết main, không dùng package. 0 <= price, quantity <= 10^9.',
         [('', '21\n','System.out.println(new Product(7,3).total());'),
          ('','0\n','System.out.println(new Product(0,9).total());'),
          ('','1000000000000000000\n','System.out.println(new Product(1000000000,1000000000).total());')]),
        ('java_method','[Docker mẫu] Java method - add','java','method',
         'Chỉ nộp phương thức long add(long a, long b), trả tổng hai tham số. Không bọc trong class, không viết main và không khai báo package. |a|, |b| <= 10^12.',
         [('', '5\n','System.out.println(add(2L,3L));'),
          ('','3\n','System.out.println(add(-5L,8L));'),
          ('','2000000000000\n','System.out.println(add(1000000000000L,1000000000000L));')]),
        ('cpp_class','[Docker mẫu] C++ class - Counter','cpp','class',
         'Nộp class Counter có constructor mặc định, public void add(long long value) và public long long get() const. Giá trị ban đầu bằng 0; add cộng vào giá trị hiện tại. Không viết main.',
         [('', '5\n','Counter c; c.add(2); c.add(3); cout << c.get();'),
          ('','0\n','Counter c; cout << c.get();'),
          ('','-7\n','Counter c; c.add(-10); c.add(3); cout << c.get();')]),
        ('python_method','[Docker mẫu] Python method - factorial','python','method',
         'Nộp hàm def factorial(n) trả n! với 0 <= n <= 20. Không đọc stdin và không tự gọi hàm/in kết quả ngoài định nghĩa. Hệ thống gọi hàm bằng test code.',
         [('', '120\n','print(factorial(5))'),
          ('','1\n','print(factorial(0))'),
          ('','2432902008176640000\n','print(factorial(20))')]),
    ]


def main():
    courses=learning.load()['courses']
    course=next((c for c in courses if c['status']=='active' and c.get('code','').startswith('LTM')),None)
    course=course or next((c for c in courses if c['status']=='active'),None)
    if not course:raise SystemExit('Cần một khóa học đang hoạt động.')
    admins=read_json('admins.json',{})
    owner=next((name for name,record in admins.items() if record.get('active',True)),None)
    if not owner:raise SystemExit('Không có tài khoản quản lý đang hoạt động.')
    prepared=[]
    for slug,title,language,kind,statement,cases in samples():
        problem={'title':title,'statement':statement,'answer_kind':kind,'language':language,'template':'',
                 'points':100,'time_limit_ms':1000,'memory_limit_mb':256,'checker':'tokens',
                 'tests':[{'input':stdin,'output':output,'test_code':code,'sample':i==0,'feedback_visibility':'sample'}
                          for i,(stdin,output,code) in enumerate(cases)]}
        config=exercise_bank.configuration({'languages':language,'problems':json.dumps([problem])})
        prepared.append({'id':'q_docker_sample_'+slug,'course_id':course['id'],'course_ids':[course['id']],
                        'practice_key_version':2,'source_url':'','title':title,'statement':statement,
                        'purpose':'practical','response_type':'code','week_number':1,'published':False,
                        'archived':False,'created_by':owner,'created_at':utc_now(),'updated_at':utc_now(),
                        'programming':config})
    with learning.LOCK,atomic_transaction():
        rows=exercise_bank.bank();existing={q['id'] for q in rows}
        additions=[q for q in prepared if q['id'] not in existing]
        if additions:
            write_json(exercise_bank.BANK,rows+additions)
            audit('learning.seed_docker_samples',owner,None,{'ids':[q['id'] for q in additions],'course_id':course['id']})
    # Verify persisted configs and build every wrapper without executing student code on the host.
    saved=[q for q in exercise_bank.bank() if q['id'].startswith('q_docker_sample_')]
    for q in saved:
        p=q['programming']['problems'][0]
        source=(Path(__file__).resolve().parents[1]/'docs'/'docker-samples'/(q['id'].removeprefix('q_docker_sample_')+'.txt')).read_bytes()
        for test in p['tests']:code_templates.build(source,p['language'],p,test)
    print(json.dumps({'added':len(additions),'total_samples':len(saved),'course':course['name'],
                      'tests':sum(len(q['programming']['problems'][0]['tests']) for q in saved)},ensure_ascii=False))


if __name__=='__main__':main()
