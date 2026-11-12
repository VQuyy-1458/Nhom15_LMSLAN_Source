"""Add a separate small, repeat-safe demo; never clear or replace classroom data."""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import storage, learning, exercise_bank, course_content


def run():
    storage.initialize()
    existing=next((c for c in learning.load()['courses'] if c['code']=='DEMO-4YC'),None)
    if existing:
        print('Demo already exists:',existing['id']);return
    students=storage.read_json('students.json')
    if 'SV001' not in students:
        raise ValueError('Cần tài khoản SV001 có sẵn; script không tự tạo hoặc đổi mật khẩu.')
    admin={'role':'admin','user_id':'admin'}
    with learning.LOCK,storage.atomic_transaction():
        cid=learning.mutate(admin,'course',{'name':'Demo · Học theo tuần & Bài tập code','code':'DEMO-4YC','semester':'Học kỳ 1 · 2026–2027','student_ids':'SV001','enrollment':'selected'},{},'127.0.0.1')['id']
        def question(title,purpose,language,problem):
            return exercise_bank.manage_question(admin,'save',{'course_id':cid,'title':title,'purpose':purpose,'response_type':'code','languages':language,'problems':json.dumps([problem]),'week_number':'1' if language=='cpp' else '2'},'127.0.0.1')['id']
        total={'title':'Tổng hai số nguyên','statement':'Đọc hai số nguyên a và b (|a|, |b| ≤ 10^9), in a + b. Nộp chương trình C++ hoàn chỉnh có main.','language':'cpp','tests':[{'input':'2 3\n','output':'5','sample':True},{'input':'-10 4\n','output':'-6','sample':True},{'input':'1000000000 1000000000\n','output':'2000000000','sample':False}]}
        q1=question('C++ · Tổng hai số nguyên','practice','cpp',total)
        product={'title':'Java OOP · Lớp Product','statement':'Viết public class Product có constructor Product(String name, long price, int quantity), getName() trả tên và total() trả price * quantity. Không viết main hoặc package; hệ thống tạo chương trình kiểm thử. Giá, số lượng không âm.','language':'java','answer_kind':'class','time_limit_ms':2000,'tests':[{'input':'','test_code':'Product p = new Product("Book", 50000L, 2); System.out.println(p.getName()); System.out.println(p.total());','output':'Book\n100000','sample':True},{'input':'','test_code':'Product p = new Product("Pen", 10000L, 0); System.out.println(p.total());','output':'0','sample':False}]}
        q2=question('Java OOP · Lớp Product','practice','java',product)
        for qid in [q1,q2]:exercise_bank.manage_question(admin,'publish',{'id':qid},'127.0.0.1')
        practical=question('Thực hành C++ · Tổng hai số','practical','cpp',total)
        pid=exercise_bank.manage_session(admin,'save',{'course_id':cid,'title':'Thực hành tuần 1 · C++','response_type':'code','question_ids':json.dumps([practical]),'duration_minutes':'60','week_number':'1'},'127.0.0.1')['id']
        full={'title':'Java OOP · Sắp xếp sinh viên','statement':'Nộp chương trình Java hoàn chỉnh (có thể đặt public class J05005). Dòng đầu là n. Mỗi sinh viên gồm một dòng tên và một dòng GPA. Tạo class Student, sắp xếp GPA giảm dần và in tên cùng GPA với 2 chữ số thập phân. Nếu bằng điểm giữ thứ tự nhập. Không viết package.','language':'java','time_limit_ms':2000,'tests':[{'input':'2\nAn\n3.2\nBinh\n3.8\n','output':'Binh 3.80\nAn 3.20','sample':True},{'input':'1\nChau\n4.0\n','output':'Chau 4.00','sample':False}]}
        question('Thi Java · Chương trình OOP hoàn chỉnh','exam','java',full)
        exercise_bank.manage_question(admin,'save',{'course_id':cid,'title':'Báo cáo TCP handshake','purpose':'practical','response_type':'file','statement':'Giải thích ba bước bắt tay TCP và nộp bản PDF hoặc TXT.','extensions':'.pdf .txt','week_number':'2'},'127.0.0.1')
        material=learning.mutate(admin,'material',{'course_id':cid,'title':'Hướng dẫn dùng khu học theo tuần','description':'Đọc hướng dẫn, làm bài tự luyện; phiên thực hành chỉ hiện sau khi giảng viên mở.','week_number':'1'},{'file':{'filename':'huong-dan.txt','data':'1. Vào Nội dung theo tuần.\n2. Mở bài tự luyện để code và chạy test mẫu.\n3. Submit để lưu bài và chấm toàn bộ test.\n4. Chờ giảng viên mở phiên để làm bài thực hành có thời lượng.\n'.encode('utf-8')}},'127.0.0.1')['id']
        assignment=learning.mutate(admin,'assignment',{'course_id':cid,'title':'Bài tập tuần 1 · Mô tả thuật toán','description':'Trình bày thuật toán cộng hai số và ba bộ dữ liệu kiểm thử. Nộp TXT/PDF hoặc ZIP.','due_at':(datetime.now(timezone.utc)+timedelta(days=7)).isoformat(),'max_attempts':'3','week_number':'1'},{},'127.0.0.1')['id']
        notice=learning.mutate(admin,'event',{'course_id':cid,'title':'Cách thử bản demo','description':'Tự luyện luôn mở và không tính điểm. Giảng viên mở phiên Thực hành tuần 1 trong mục Bài tập để sinh viên thử giờ làm bài chung.','kind':'announcement','starts_at':storage.utc_now(),'week_number':'1'},{},'127.0.0.1')['id']
        for n,title,lesson,reading,mids,aids,codeids,notices in [(1,'Tuần 1 · Nhập xuất và test case','Ôn stdin/stdout, kiểu long long và test biên.','Đọc hướng dẫn; thử số âm và trường hợp tổng lớn.',[material],[assignment],['practice_'+q1,pid],[notice]),(2,'Tuần 2 · Java hướng đối tượng','Constructor, đóng gói dữ liệu, phương thức và chương trình có main.','Đọc đề Product và phân biệt dạng class với program.',[],[],['practice_'+q2],[])]:
            course_content.save(admin,{'course_id':cid,'week_number':str(n),'title':title,'lesson_text':lesson,'reading_text':reading,'material_ids':json.dumps(mids),'assignment_ids':json.dumps(aids),'activity_ids':json.dumps(codeids),'announcement_ids':json.dumps(notices)},'127.0.0.1')
    print('Created demo:',cid,'student SV001; practical remains a private draft.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    if not args.apply:parser.error('Dùng --apply để thêm khóa demo, không thay dữ liệu cũ.')
    run()
