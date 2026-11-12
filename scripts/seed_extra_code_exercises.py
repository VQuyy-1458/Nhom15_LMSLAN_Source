"""Add 20 original, standard-input Python exercises without replacing existing data."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import storage,learning,exercise_bank

# Title, statement, reference program, hand-checked input/output examples.
TASKS=[
('Tổng hai số','Đọc hai số nguyên a, b; in a+b.','a,b=map(int,input().split());print(a+b)',[('2 3','5'),('-10 4','-6'),('1000000000 1000000000','2000000000')]),
('Hiệu hai số','Đọc hai số nguyên a, b; in a-b.','a,b=map(int,input().split());print(a-b)',[('7 3','4'),('-1 8','-9'),('0 0','0')]),
('Tích hai số','Đọc hai số nguyên a, b; in a*b.','a,b=map(int,input().split());print(a*b)',[('7 3','21'),('-4 8','-32'),('0 9','0')]),
('Chẵn hay lẻ','Đọc số nguyên n; in EVEN nếu n chẵn, ngược lại in ODD.','n=int(input());print("EVEN" if n%2==0 else "ODD")',[('0','EVEN'),('-3','ODD'),('24','EVEN')]),
('Số lớn nhất','Đọc ba số nguyên; in số lớn nhất.','print(max(map(int,input().split())))',[('1 2 3','3'),('-2 -5 -1','-1'),('9 9 2','9')]),
('Giá trị tuyệt đối','Đọc số nguyên n; in |n|.','print(abs(int(input())))',[('-42','42'),('0','0'),('11','11')]),
('Tổng từ 1 đến n','Đọc n không âm; in tổng 1+2+...+n.','n=int(input());print(n*(n+1)//2)',[('0','0'),('5','15'),('100000','5000050000')]),
('Tổng chữ số','Đọc số nguyên không âm n; in tổng các chữ số.','print(sum(map(int,input().strip())))',[('0','0'),('12345','15'),('90909','27')]),
('Đếm chữ số','Đọc số nguyên không âm n; in số chữ số trong biểu diễn thập phân.','print(len(input().strip()))',[('0','1'),('101','3'),('99999','5')]),
('Đảo chữ số','Đọc số nguyên không âm n; in số nhận được sau khi đảo chữ số, bỏ số 0 đầu.','print(int(input().strip()[::-1]))',[('1200','21'),('7','7'),('12345','54321')]),
('Ước chung lớn nhất','Đọc hai số nguyên không âm a, b, không đồng thời bằng 0; in ước chung lớn nhất.','import math\na,b=map(int,input().split());print(math.gcd(a,b))',[('12 18','6'),('0 9','9'),('17 13','1')]),
('Bội chung nhỏ nhất','Đọc hai số nguyên dương a, b; in bội chung nhỏ nhất.','import math\na,b=map(int,input().split());print(a//math.gcd(a,b)*b)',[('12 18','36'),('1 9','9'),('17 13','221')]),
('Kiểm tra số nguyên tố','Đọc n (0 ≤ n ≤ 10^9); in YES nếu n là số nguyên tố, ngược lại NO.','import math\nn=int(input());print("YES" if n>=2 and all(n%d for d in range(2,math.isqrt(n)+1)) else "NO")',[('1','NO'),('2','YES'),('97','YES'),('99','NO')]),
('Đếm số chẵn','Đọc n rồi n số nguyên; in số lượng số chẵn. Các số có thể trải trên nhiều dòng.','import sys\na=list(map(int,sys.stdin.read().split()));print(sum(x%2==0 for x in a[1:1+a[0]]))',[('5\n1 2 3 4 6','3'),('3\n1 3 5','0'),('2\n-2 0','2')]),
('Tổng mảng','Đọc n rồi n số nguyên; in tổng các phần tử. Các số có thể trải trên nhiều dòng.','import sys\na=list(map(int,sys.stdin.read().split()));print(sum(a[1:1+a[0]]))',[('3\n1 2 3','6'),('4\n-5 2 1 2','0'),('1\n1000000000','1000000000')]),
('Phần tử lớn nhất','Đọc n ≥ 1 rồi n số nguyên; in phần tử lớn nhất.','import sys\na=list(map(int,sys.stdin.read().split()));print(max(a[1:1+a[0]]))',[('3\n1 2 3','3'),('3\n-8 -1 -9','-1'),('1\n0','0')]),
('Đếm nguyên âm','Đọc một dòng văn bản ASCII; đếm các nguyên âm a,e,i,o,u, không phân biệt hoa thường.','s=input().lower();print(sum(c in "aeiou" for c in s))',[('Hello World','3'),('AEIOU','5'),('xyz','0')]),
('Chuỗi đối xứng','Đọc một dòng chuỗi ASCII; in YES nếu chuỗi giống chuỗi đảo ngược, ngược lại NO. Có phân biệt hoa thường và khoảng trắng.','s=input();print("YES" if s==s[::-1] else "NO")',[('abba','YES'),('abc','NO'),('A a','NO')]),
('Đếm từ','Đọc một dòng; các từ cách nhau bởi một hoặc nhiều dấu cách. In số từ.','print(len(input().split()))',[('hello world','2'),('  a   b c  ','3'),('','0')]),
('Sắp xếp tăng dần','Đọc n ≥ 1 rồi n số nguyên; in các số tăng dần, cách nhau bởi dấu cách.','import sys\na=list(map(int,sys.stdin.read().split()));print(*sorted(a[1:1+a[0]]))',[('5\n4 2 2 -1 3','-1 2 2 3 4'),('1\n0','0'),('3\n9 8 7','7 8 9')]),
]

def run():
    storage.initialize();admin={'role':'admin','user_id':'admin'}
    marker=storage.read_json('shared_catalogue_20261111.json',{});cid=marker.get('courses',{}).get('python')
    if not cid:raise RuntimeError('Không tìm thấy khóa Python của bộ dữ liệu mẫu.')
    count=0
    with learning.LOCK,storage.atomic_transaction():
        for index,(title,description,solution,cases) in enumerate(TASKS,1):
            key=f'extra-python-{index:02}';name='Python cơ bản · '+title
            if any(q.get('seed_key')==key for q in exercise_bank.bank()):continue
            tests=[]
            for n,(inp,out) in enumerate(cases):
                result=subprocess.run([sys.executable,'-c',solution],input=inp+'\n',text=True,capture_output=True,timeout=5,encoding='utf8')
                if result.returncode or result.stdout.split()!=out.split():raise RuntimeError(f'Test sai: {name} {inp!r} {result.stderr}')
                tests.append({'input':inp+'\n','output':out+'\n','sample':n==0})
            problem={'title':name,'statement':description+'\nNộp chương trình Python 3 hoàn chỉnh, đọc stdin và in kết quả ra stdout.','language':'python','time_limit_ms':2000,'memory_limit_mb':256,'tests':tests}
            qid=exercise_bank.manage_question(admin,'save',{'title':name,'statement':problem['statement'],'course_ids':json.dumps([cid]),'purpose':'practice','response_type':'code','languages':'python','problems':json.dumps([problem])},'127.0.0.1')['id']
            rows=exercise_bank.bank();next(q for q in rows if q['id']==qid)['seed_key']=key;storage.write_json(exercise_bank.BANK,rows)
            exercise_bank.manage_question(admin,'publish',{'id':qid},'127.0.0.1');count+=1
    print(f'Đã thêm {count} bài Python gốc vào kho chung và bật luyện tập cho khóa Python; 20 bài có thể gắn thêm vào khóa khác.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    if not args.apply:parser.error('Dùng --apply để thêm dữ liệu.')
    run()
