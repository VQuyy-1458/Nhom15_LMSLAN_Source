"""Add the sourced shared catalogue once, preserving later teacher customizations."""
import argparse
import json
import sys
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import storage,learning,exercise_bank,question_papers,exam_catalog,course_content,course_schedule
MARKER='shared_catalogue_20261111.json'

def run():
    storage.initialize()
    if storage.read_json(MARKER,{}).get('complete'):
        print('Already seeded; preserving teacher changes.');return
    source=json.loads((ROOT/'resources/code_catalogue/questions.json').read_text(encoding='utf8'))
    admin={'role':'admin','user_id':'admin'};ip='127.0.0.1'
    students=[sid for sid,s in storage.read_json('students.json').items() if s.get('active',True)]
    if 'SV001' in students:students.remove('SV001');students.insert(0,'SV001')
    students=students[:16]
    if not students:raise ValueError('Need an existing student account.')
    with learning.LOCK,storage.atomic_transaction():
        old=exercise_bank.bank()
        # Retire only the previous managed demo's questions; keep attempts/history.
        demo_ids={c['id'] for c in learning.load()['courses'] if c['code']=='DEMO-4YC'}
        for q in old:
            if q.get('course_id') in demo_ids:q.update(archived=True,published=False)
        storage.write_json(exercise_bank.BANK,old)
        courses={};qids={};papers={}
        for lang,name,code,weekday in [('cpp','Lập trình C++ · Thuật toán','CPP-2026',2),('java','Java · Lập trình hướng đối tượng','JAVA-OOP-2026',4),('python','Python · Xử lý dữ liệu','PY-2026',6)]:
            cid=learning.mutate(admin,'course',{'name':name,'code':code,'semester':'Học kỳ 1 · 2026–2027','student_ids':','.join(students),'enrollment':'selected'},{},ip)['id'];courses[lang]=cid
            group=[r for r in source if r['language']==lang]
            for idx,r in enumerate(group):
                form={'title':r['title'],'statement':r['statement'],'course_ids':json.dumps([cid]),'purpose':'practice' if r['practice'] else 'practical' if idx<14 else 'exam','response_type':'code','languages':lang,'problems':json.dumps(r['programming']['problems']),'source_url':r['source_url'],'week_number':str(min(12,idx//2+1))}
                qid=exercise_bank.manage_question(admin,'save',form,ip)['id'];qids[r['key']]=qid
                if r['practice']:exercise_bank.manage_question(admin,'publish',{'id':qid},ip)
            ids=[qids[r['key']] for r in group if not r['practice']]
            def paper(title,selected):
                pid=question_papers.manage(admin,'save',{'title':title,'response_type':'code','question_ids':json.dumps(selected),'description':'Đề từ kho chung; tự chấm bằng Docker, giữ mọi lần nộp.'},ip)['id'];question_papers.manage(admin,'publish',{'id':pid},ip);return pid
            pool=paper(name+' · Ngân hàng thực hành',ids[:6]);a=paper(name+' · Mã đề A',ids[6:9]);b=paper(name+' · Mã đề B',ids[9:12]);papers[lang]=[pool,a,b]
            exercise_bank.manage_session(admin,'save',{'course_id':cid,'title':'Thực hành 01 · Bốc 2 bài từ kho','response_type':'code','paper_ids':json.dumps([pool]),'paper_distribution':'random_questions','questions_per_student':'2','duration_minutes':'60','week_number':'5'},ip)
            exam_catalog.save(admin,{'course_id':cid,'title':'Thi thử · Phát mã đề A/B','type':'programming','assessment_type':'test','paper_ids':json.dumps([a,b]),'paper_distribution':'random_papers','duration_minutes':'90','participant_ids':'\n'.join(students)},ip)
            exam_catalog.save(admin,{'course_id':cid,'title':'Giữa kỳ · Chọn 2 câu','type':'programming','assessment_type':'midterm','paper_ids':json.dumps([pool]),'paper_distribution':'random_questions','questions_per_student':'2','duration_minutes':'60','participant_ids':'\n'.join(students)},ip)
            today=date(2026,11,11);monday=today-timedelta(days=today.weekday());last=monday+timedelta(weeks=11)
            week=lambda day:f'{day.isocalendar().year}-W{day.isocalendar().week:02}'
            course_schedule.bulk(admin,{'course_id':cid,'title':name+' · Buổi học','start_week':week(monday),'end_week':week(last),'weekday':str(weekday),'start_time':'07:30','end_time':'10:00','location':'Phòng máy LAN'},ip)
            material=learning.mutate(admin,'material',{'course_id':cid,'title':'Hướng dẫn học và nộp bài','description':'Tự luyện không tính điểm. Thực hành chỉ hiện khi giảng viên mở; mọi lần Submit được lưu. Điểm danh LAN dựa vào tài khoản đang đăng nhập.','week_number':'1'},{'file':{'filename':'huong-dan.txt','data':('Khóa '+name+'\nCác bài có ghi nguồn gốc. Đọc đúng quy định program / class trước khi nộp.\nChạy test mẫu trước rồi Submit. Luyện tập không tính điểm.\n').encode('utf8')}},ip)['id']
            assignment=learning.mutate(admin,'assignment',{'course_id':cid,'title':'Báo cáo phân tích thuật toán / thiết kế lớp','description':'Chọn một bài đã làm, giải thích thuật toán hoặc thiết kế class, nêu test biên và nhận xét kết quả. Nộp PDF/TXT/ZIP.','due_at':(datetime.now(timezone.utc)+timedelta(days=14)).isoformat(),'max_attempts':'6','week_number':'2'},{},ip)['id']
            for n in range(1,13):
                selected=[r for r in group if r['practice'] and min(12,group.index(r)//2+1)==n]
                activities=[exercise_bank.practice_id(next(q for q in exercise_bank.bank() if q['id']==qids[r['key']]),cid) for r in selected]
                course_content.save(admin,{'course_id':cid,'week_number':str(n),'title':f'Tuần {n} · '+('Nền tảng và luyện tập' if n<5 else 'Thực hành và vận dụng'),'lesson_text':f'Học nội dung tuần {n} của {name}. Phân tích yêu cầu, thiết kế lời giải, kiểm thử và xem phản hồi chấm.','reading_text':'Đọc đề và hợp đồng dữ liệu, xem ví dụ mẫu, bổ sung tình huống biên trước khi nộp.','material_ids':json.dumps([material] if n==1 else []),'assignment_ids':json.dumps([assignment] if n==2 else []),'activity_ids':json.dumps(activities)},ip)
        storage.write_json(MARKER,{'complete':True,'courses':courses,'questions':qids,'papers':papers,'created_at':storage.utc_now()})
    print(json.dumps({'courses':courses,'questions':len(qids),'practice':20,'private':40,'students':students},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    if not args.apply:p.error('Use --apply to add data (existing records are preserved).')
    run()
