"""Reusable immutable papers, exam snapshots and stable per-student distribution."""
import copy
import json
import math
import random
import secrets
from pathlib import Path
from . import learning, exercise_bank
from .storage import read_json,write_json,utc_now,atomic_transaction,audit,save_payload

STORE='question_papers.json'
MODES={'same','random_questions','random_papers'}


def listing():return read_json(STORE,[])


def question_ids(form):
    from .course_content import ids
    return ids(form,'question_ids')


def selected(ids,kind):
    available={q['id']:q for q in exercise_bank.bank()};result=[]
    for qid in ids:
        q=available.get(qid)
        if not q or q.get('archived') or q['response_type']!=kind:
            raise learning.LearningError(400,'Câu hỏi đã ẩn/lưu trữ hoặc không đúng hình thức của đề.')
        result.append(q)
    if not result:raise learning.LearningError(400,'Chọn ít nhất một câu trong kho chung.')
    return result


def manage(session,action,form,ip):
    exercise_bank.staff(session)
    with learning.LOCK,atomic_transaction():
        rows=listing();old=next((r for r in rows if r['id']==form.get('id')),None)
        if (form.get('id') or action!='save') and not old:raise learning.LearningError(404,'Không tìm thấy đề.')
        if action=='save':
            if old and old['state']!='draft':raise learning.LearningError(409,'Đề đã công bố không sửa trực tiếp; tạo bản sao để chỉnh.')
            kind=form.get('response_type','code')
            if kind not in {'code','file'}:raise learning.LearningError(400,'Hình thức đề không hợp lệ.')
            questions=selected(question_ids(form),kind)
            row={'id':old['id'] if old else 'paper_'+secrets.token_hex(10),'title':learning.text(form,'title'),
                 'response_type':kind,'description':learning.text(form,'description',10000,False),
                 'question_ids':[q['id'] for q in questions],'questions':copy.deepcopy(questions),
                 'state':'draft','created_at':old['created_at'] if old else utc_now(),'updated_at':utc_now(),
                 'created_by':session['user_id'],'version':old.get('version',1) if old else 1}
            if kind=='code':row['programming']=exercise_bank.combined(questions)
            rows=[r for r in rows if r['id']!=row['id']]+[row]
        elif action=='publish':
            row=old
            if row['state']!='draft':raise learning.LearningError(409,'Chỉ công bố đề nháp.')
            row.update(state='published',published_at=utc_now())
        elif action=='archive':
            row=old;row.update(state='archived',archived_at=utc_now())
        elif action=='clone':
            row=copy.deepcopy(old);row.update(id='paper_'+secrets.token_hex(10),title=old['title']+' · bản sao',state='draft',
                parent_id=old['id'],version=old.get('version',1)+1,created_at=utc_now(),created_by=session['user_id'])
            rows.append(row)
        else:raise learning.LearningError(400,'Thao tác đề không hợp lệ.')
        write_json(STORE,rows);audit('learning.paper_'+action,session['user_id'],ip,{'id':row['id']})
        return {'ok':True,'id':row['id'],'state':row['state']}


def resolve(form,kind):
    from .course_content import ids
    paper_ids=ids(form,'paper_ids') if form.get('paper_ids') else ([form['paper_id']] if form.get('paper_id') else [])
    if not paper_ids:return None
    available={p['id']:p for p in listing()};papers=[]
    for pid in dict.fromkeys(paper_ids):
        p=available.get(pid)
        if not p or p['state']!='published' or p['response_type']!=kind:
            raise learning.LearningError(409,'Chọn đề đã công bố, chưa lưu trữ và đúng hình thức.')
        papers.append(copy.deepcopy(p))
    mode=form.get('paper_distribution','same')
    if mode not in MODES:raise learning.LearningError(400,'Cách phát đề không hợp lệ.')
    if mode=='same' and len(papers)!=1:raise learning.LearningError(400,'Phát cùng đề cần chọn một đề duy nhất.')
    if mode=='random_papers' and len(papers)<2:raise learning.LearningError(400,'Phát các mã đề khác nhau cần chọn ít nhất hai đề.')
    unique={};variants=[]
    for paper in papers:
        indices=[]
        for q in paper['questions']:
            specs=q['programming']['problems'] if kind=='code' else [q]
            for index,spec in enumerate(specs):
                key=(q['id'],index)
                if key not in unique:
                    item=copy.deepcopy(spec);item.update(source_question_id=q['id'],source_problem_index=index)
                    unique[key]=item
                indices.append(list(unique).index(key))
        variants.append({'id':paper['id'],'title':paper['title'],'indices':list(dict.fromkeys(indices))})
    maximum=len(unique)
    count=learning.integer(form,'questions_per_student',maximum,1,maximum)
    result={'paper_ids':[p['id'] for p in papers],'paper_snapshots':papers,'paper_variants':variants,
            'paper_distribution':mode,'questions_per_student':count}
    if kind=='code':
        languages=set(papers[0]['programming']['languages'])
        for paper in papers:languages.intersection_update(paper['programming']['languages'])
        if not languages:raise learning.LearningError(400,'Các mã đề cần có ngôn ngữ chạy tương thích.')
        config=exercise_bank.configuration({'languages':','.join(sorted(languages)),'problems':json.dumps(list(unique.values()))})
        for cleaned,raw in zip(config['problems'],unique.values()):
            cleaned.update(source_question_id=raw['source_question_id'],source_problem_index=raw['source_problem_index'])
        result['programming']=config
    else:result['file_questions']=list(unique.values())
    return result


def indices(row,sid):
    count=len(row.get('programming',{}).get('problems',row.get('file_questions',[])))
    if row.get('paper_distribution','same')=='same':return list(range(count))
    return [i for i in row.get('student_problem_sets',{}).get(sid,[]) if isinstance(i,int) and not isinstance(i,bool) and 0<=i<count]


def distribute(row):
    """Called once on release under the same transaction as opening the session."""
    count=len(row.get('programming',{}).get('problems',row.get('file_questions',[])))
    mode=row.get('paper_distribution','same');students=list(row['participants']);rng=random.SystemRandom()
    if mode=='same':return
    if row.get('student_problem_sets'):
        if set(row['student_problem_sets'])!=set(students):raise learning.LearningError(409,'Danh sách đã phát đề thay đổi; hãy tạo lượt mới.')
        return
    assigned={};codes={}
    if mode=='random_papers':
        variants=list(row['paper_variants']);rng.shuffle(students);rng.shuffle(variants)
        for i,sid in enumerate(students):
            paper=variants[i%len(variants)];assigned[sid]=paper['indices'];codes[sid]=paper['id']
    elif mode=='random_questions':
        amount=row['questions_per_student'];capacity=math.comb(count,amount);used=set()
        for sid in students:
            if len(used)>=capacity:used.clear()
            choice=tuple(sorted(rng.sample(range(count),amount)))
            for _ in range(50):
                if choice not in used:break
                choice=tuple(sorted(rng.sample(range(count),amount)))
            used.add(choice);assigned[sid]=list(choice)
    else:raise learning.LearningError(400,'Chế độ phát đề không hợp lệ.')
    row.update(student_problem_sets=assigned,student_papers=codes,distributed_at=utc_now())


def materialize_file_exam(row):
    from .config import EXAM_DIR
    variants=row.get('paper_variants',[]);questions=row.get('file_questions',[])
    if not variants:return
    names=[];nonce=secrets.token_hex(5)
    for variant in variants:
        content=[row['title'],variant['title'],'']
        for n,index in enumerate(variant['indices'],1):
            q=questions[index];content.extend([f'Câu {n}. {q["title"]}',q['statement'],''])
        name='paper_'+row['id']+'_'+nonce+'_'+str(len(names)+1)+'.txt'
        EXAM_DIR.mkdir(parents=True,exist_ok=True);save_payload(EXAM_DIR/name,'\n'.join(content).encode('utf-8'));names.append(name)
    row['paper_files']=names


def file_distribution(settings,student_ids):
    """Feed bank papers into the existing file release/receipt engine."""
    import hashlib
    from .config import EXAM_DIR
    catalog=read_json('exam_catalog.json',[])
    row=next((r for r in catalog if r['id']==settings.get('exam_catalog_id')),None)
    if not row or not row.get('paper_ids'):return None
    row['participants']=list(student_ids);distribute(row);assignments={};files=set()
    for sid in student_ids:
        chosen=indices(row,sid)
        # Same-mode file papers are one published variant, not the combined pool.
        if row.get('paper_distribution','same')=='same':chosen=row['paper_variants'][0]['indices']
        chunks=[row['title'],'']
        for n,index in enumerate(chosen,1):
            q=row['file_questions'][index];chunks.extend([f'Câu {n}. {q["title"]}',q['statement'],''])
        content='\n'.join(chunks).encode('utf-8')
        name='paper_'+row['id']+'_'+hashlib.sha256(content).hexdigest()[:20]+'.txt'
        path=EXAM_DIR/name;EXAM_DIR.mkdir(parents=True,exist_ok=True)
        if not path.exists():save_payload(path,content)
        assignments[sid]=name;files.add(name)
    row['paper_files']=sorted(files);settings['exam_paper_files']=row['paper_files']
    write_json('exam_catalog.json',catalog)
    return assignments
