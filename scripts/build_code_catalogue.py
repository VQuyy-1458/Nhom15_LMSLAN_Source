"""Build a reproducible 60-question catalogue from downloaded official sources.

Run fetch_catalogue_sources.py first. No downloaded solutions are executed.
"""
from pathlib import Path
import hashlib
import json
import random
import sys
from html.parser import HTMLParser
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.exam_catalog import validate_programming
from scripts import catalogue_cpp as cpp, catalogue_java as java, catalogue_python as py

CACHE=ROOT/'backups/problem-sources-20261111'
OUT=ROOT/'resources/code_catalogue'
JAVA=list(java.REFS)
PYTHON=list(py.DESCRIPTIONS)

def canonical(slug):
    path=CACHE/'spec'/slug/'canonical-data.json';doc=json.loads(path.read_text(encoding='utf8'));leaves=[]
    def walk(cases):
        for c in cases:
            if 'cases' in c:walk(c['cases'])
            else:leaves.append(c)
    walk(doc['cases']);return leaves,hashlib.sha256(path.read_bytes()).hexdigest()

def choose(cases,limit):
    # Deterministic, stratified by API property and successful/error results.
    groups=defaultdict(list)
    for c in cases:groups[(c['property'],isinstance(c['expected'],dict) and 'error' in c['expected'])].append(c)
    result=[]
    while len(result)<min(limit,len(cases)):
        for group in groups.values():
            if group and len(result)<limit:result.append(group.pop(0))
    return result

def normalized(v):
    if isinstance(v,dict):return 'ERROR' if 'error' in v else {k:normalized(x) for k,x in v.items()}
    if isinstance(v,list):return [normalized(x) for x in v]
    if isinstance(v,float):return round(v,6)
    return v

class Samples(HTMLParser):
    def __init__(self):super().__init__();self.active=False;self.blocks=[]
    def handle_starttag(self,tag,attrs):
        if tag=='pre':self.active=True;self.blocks.append('')
        if tag=='br' and self.active:self.blocks[-1]+='\n'
    def handle_endtag(self,tag):
        if tag=='pre':self.active=False
    def handle_data(self,text):
        if self.active:self.blocks[-1]+=text

def question(key,title,language,statement,tests,reference,source,practice,**kwargs):
    problem={'title':title,'statement':statement,'language':language,'points':100,'time_limit_ms':3000,'memory_limit_mb':256,'checker':'json' if language!='cpp' else 'tokens','tests':tests,**kwargs}
    config=validate_programming({'languages':language,'problems':json.dumps([problem])})
    extension={'java':'java','cpp':'cpp','python':'py'}[language]
    ref='references/'+key+'.'+extension;path=OUT/ref;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(reference,encoding='utf8')
    return {'key':key,'title':title,'language':language,'statement':statement,'programming':config,'reference':ref,'source_url':source,'practice':practice,'suggested_purpose':'practice' if practice else 'practical','week_number':1 if practice else 5}

def build():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    for idx,(task,(name,description)) in enumerate(cpp.TASKS.items()):
        parser=Samples();source=CACHE/'cses'/f'{task}.html';parser.feed(source.read_text(encoding='utf8'));assert len(parser.blocks)>=2,task
        sample_in,sample_out=parser.blocks[:2];cases=[{'input':sample_in,'output':sample_out,'sample':True}]
        # Recheck official samples against an independent oracle.
        assert str(cpp.expected(task,sample_in)).split()==sample_out.split(),task
        for text in cpp.cases(task):cases.append({'input':text,'output':str(cpp.expected(task,text))+'\n','sample':False})
        desc=description+'\nNộp chương trình C++17 hoàn chỉnh có main. Dùng số nguyên 64-bit khi cần.\nNguồn: CSES '+name+' (diễn giải tiếng Việt, giữ stdin/stdout gốc).'
        row=question('cses-'+str(task),'C++ · '+name,'cpp',desc,cases,cpp.CPP.replace('__ID__',str(task)),f'https://cses.fi/problemset/task/{task}/',idx<7)
        row['provenance']={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'license':'CSES: short independently written Vietnamese restatement; official sample attributed.'};rows.append(row)
    for idx,slug in enumerate(JAVA):
        allcases,sha=canonical(slug)
        if slug=='bank-account':allcases=[c for c in allcases if not any(o['operation']=='concurrent' for o in c['input']['operations'])]
        # Upstream case marks property roster but expects a grade query (desiredGrade=2); exclude this inconsistent fixture.
        if slug=='grade-school':allcases=[c for c in allcases if c.get('uuid')!='c125dab7-2a53-492f-a99a-56ad511940d8']
        if slug=='reverse-string':allcases=[c for c in allcases if c['input']['value'].isascii()]
        cases=[];selected=choose(allcases,12)
        for j,c in enumerate(selected):
            test={'input':'','test_code':java.test_code(slug,c),'output':json.dumps(normalized(c['expected']),ensure_ascii=False),'sample':j<2}
            if slug in java.PROGRAMS:
                test['test_code']='';key={'raindrops':'number','reverse-string':'value','scrabble-score':'word'}[slug];test['input']=str(c['input'][key])+'\n'
            if slug=='triangle' and (min(c['input']['sides'])<=0 or 2*max(c['input']['sides'])>=sum(c['input']['sides'])):test['output']='"ERROR"'
            cases.append(test)
        desc=java.CONTRACTS[slug]+'\n'+('' if slug in java.PROGRAMS else 'Nộp toàn bộ class theo API trên, không package, không cần main. Template của giảng viên tạo main, khởi tạo đối tượng và gọi method. Phương thức/constructor phải truy cập được từ cùng package. Hệ thống so sánh giá trị JSON; số thực làm tròn 6 chữ số thập phân trước khi in.\n')+'Nguồn: Exercism Java / '+slug+' (MIT); yêu cầu được diễn giải, giao thức chấm nêu tại đây.'
        row=question('java-'+slug,'Java · '+slug.replace('-',' ').title(),'java',desc,cases,java.program(slug) if slug in java.PROGRAMS else java.REFS[slug],f'https://exercism.org/tracks/java/exercises/{slug}',idx<7,answer_kind='program' if slug in java.PROGRAMS else 'class',template='' if slug in java.PROGRAMS else java.TEMPLATE)
        row['provenance']={'canonical_sha256':sha,'canonical_case_ids':[c.get('uuid') for c in selected],'license':'MIT · Exercism Java / problem-specifications'};rows.append(row)
    for idx,slug in enumerate(PYTHON):
        allcases,sha=canonical(slug);selected=choose(allcases,16);cases=[]
        for j,c in enumerate(selected):cases.append({'input':json.dumps({'property':c['property'],'input':c['input']},ensure_ascii=False)+'\n','output':json.dumps(normalized(c['expected']),ensure_ascii=False)+'\n','sample':j<2})
        desc='Nộp chương trình Python 3 hoàn chỉnh. Stdin chứa một JSON object có hai khóa property và input (định dạng chuyển thể để học xử lý dữ liệu). Stdout in một giá trị JSON hợp lệ, không in lời nhắc; thứ tự khóa object không quan trọng, thứ tự mảng phải đúng.\n'+py.DESCRIPTIONS[slug]+'\nNguồn: Exercism Python / '+slug+' (MIT). Đề gốc là bài hàm; bản này chuyển thành chương trình stdin/stdout JSON, dùng dữ liệu chuẩn từ problem-specifications.'
        row=question('python-'+slug,'Python · '+slug.replace('-',' ').title(),'python',desc,cases,py.SOLVER.replace('__SLUG__',repr(slug)),f'https://exercism.org/tracks/python/exercises/{slug}',idx<6)
        row['provenance']={'canonical_sha256':sha,'canonical_case_ids':[c.get('uuid') for c in selected],'license':'MIT · Exercism Python / problem-specifications'};rows.append(row)
    assert len(rows)==60 and sum(r['practice'] for r in rows)==20
    (OUT/'questions.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for source,target in [('spec/LICENSE','LICENSE-specifications.txt'),('java/LICENSE','LICENSE-java.txt'),('python/LICENSE','LICENSE-python.txt')]:
        (OUT/target).write_bytes((CACHE/source).read_bytes())
    (OUT/'README.md').write_text('''# Bộ 60 bài code LAN-LMS

20 C++ (CSES), 20 Java (Exercism, gồm 17 class OOP và 3 program hoàn chỉnh), 20 Python (Exercism chuyển thể stdin/stdout JSON).
Mặc định 20 bài cho luyện tập, 40 bài riêng tư. Đây là một kho chung: giảng viên đổi liên kết khóa học, bật/tắt luyện tập và dùng lại bất kỳ bài nào trong đề thực hành/thi.

Mỗi bài có URL gốc, hash bản nguồn, test mẫu và test ẩn. CSES được viết lại ngắn bằng tiếng Việt; ví dụ gốc có ghi nguồn. Exercism dùng MIT, giấy phép kèm thư mục này. Các lời giải tham chiếu tự viết phục vụ xác minh, không phục vụ qua API sinh viên.

Các bản chuyển thể nêu rõ giao thức và phạm vi trong từng đề. Java Reverse String giới hạn ASCII; Bank Account kiểm thử tuần tự, không tuyên bố chấm concurrency. JSON checker so sánh cấu trúc, phân biệt boolean và number, không chấp nhận JSON không hợp lệ.

Tái tạo: `python scripts/fetch_catalogue_sources.py`, `python scripts/build_code_catalogue.py`. Kiểm chứng lời giải trong Docker: `python scripts/validate_code_catalogue.py`. Nạp dữ liệu: `python scripts/seed_shared_catalogue.py --apply` (nên dừng server trước khi nạp).
''',encoding='utf8')
    print(f'Built {len(rows)} questions, {sum(len(r["programming"]["problems"][0]["tests"]) for r in rows)} tests, 20 practice.')

if __name__=='__main__':build()
