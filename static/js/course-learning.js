/* Weekly plans, compact resources and separately published practice/practical work. */
(() => {
  'use strict';
  const esc=window.cssEscape, states=new Map();let context;
  const names={practice:'Luyện tập',practical:'Thực hành',exam:'Thi'}, formats={code:'Code',file:'Nộp file'};
  const date=v=>v?new Date(v).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh',dateStyle:'short',timeStyle:'short'}):'Chưa đặt lịch';
  const label=n=>Number(n)?'Tuần '+n:'Chưa gắn tuần';
  const state=id=>{if(!states.has(id))states.set(id,{q:'',week:'',kind:'',page:1});return states.get(id);};
  function assignedWeeks(data,row,type){const key={material:'material_ids',assignment:'assignment_ids',code:'activity_ids'}[type];return [...new Set([...(row.week_number?[row.week_number]:[]),...(data.course_weeks||[]).filter(w=>w.course_id===row.course_id&&(w[key]||[]).includes(row.id)).map(w=>w.week_number)])].sort((a,b)=>a-b);}
  const rowWeeks=(r,type)=>{const values=assignedWeeks(context.data,r,type);return values.length?values.map(label).join(', '):label(0);};
  const badge=(text,cls='')=>`<span class="student-status ${cls}">${esc(text)}</span>`;
  const empty=text=>`<p class="cl-empty">${esc(text)}</p>`;
  const selectOptions=(rows,value)=>rows.map(([id,title])=>`<option value="${esc(id)}" ${String(id)===String(value)?'selected':''}>${esc(title)}</option>`).join('');
  function bindContext(data,cid,admin){context={data,cid,admin};}
  function weeks(data,cid){
    const numbers=new Set((data.course_weeks||[]).filter(w=>w.course_id===cid).map(w=>w.week_number));
    for(const key of ['materials','assignments','events','practicals'])for(const r of data[key]||[])if(r.course_id===cid&&r.week_number)numbers.add(r.week_number);
    for(const r of data.programming?.exams||[])if(r.course_id===cid&&r.week_number)numbers.add(r.week_number);
    return [...numbers].sort((a,b)=>a-b);
  }
  function weekly(data,cid,admin){
    bindContext(data,cid,admin);const c=data.courses.find(c=>c.id===cid),numbers=weeks(data,cid);
    const activities=admin?data.code_activities||[]:data.programming?.exams||[];
    return `<section class="panel cl-plan"><div class="cl-heading"><div><h2>Nội dung theo tuần</h2><p class="muted">Bài học, bài đọc và các việc cần làm theo tiến độ khóa học.</p></div>${admin&&c.status!=='completed'?'<button class="btn btn-primary" data-week-edit="new"><i aria-hidden="true" class="fa fa-plus"></i> Thêm tuần học</button>':''}</div>${numbers.map(n=>{
      const w=(data.course_weeks||[]).find(r=>r.course_id===cid&&r.week_number===n)||{week_number:n,title:'Nội dung tuần '+n};
      const linked=(key,ids)=>data[key].filter(r=>r.course_id===cid&&(r.week_number===n||(w[ids]||[]).includes(r.id))&&!r.archived);
      const materials=linked('materials','material_ids'),assignments=linked('assignments','assignment_ids');
      const code=activities.filter(r=>r.course_id===cid&&(r.week_number===n||(w.activity_ids||[]).includes(r.id)));
      const notices=linked('events','announcement_ids').filter(r=>r.kind==='announcement');
      return `<details class="cl-week" ${n===numbers[0]?'open':''}><summary><span class="cl-week-number">${n}</span><span><strong>${esc(w.title)}</strong><small>Tuần ${n} · ${materials.length} tài liệu · ${assignments.length+code.length} bài tập</small></span></summary><div class="cl-week-body">${admin&&c.status!=='completed'?`<button class="btn btn-secondary cl-week-edit" data-week-edit="${n}">Sửa nội dung tuần</button>`:''}<div class="cl-reading"><section><h3>Bài học</h3><p>${esc(w.lesson_text||'Chưa có nội dung bài học.')}</p></section><section><h3>Bài đọc</h3><p>${esc(w.reading_text||'Chưa có bài đọc bổ sung.')}</p></section></div><h3>Tài liệu</h3>${materials.map(r=>shortRow(r,'material',admin)).join('')||empty('Chưa gắn tài liệu.')}<h3>Bài tập</h3>${assignments.map(r=>shortRow(r,'assignment',admin)).join('')}${code.map(r=>codeRow(r,admin)).join('')}${!assignments.length&&!code.length?empty('Chưa giao bài tập.'):''}${notices.length?`<h3>Thông báo tuần</h3>${notices.map(r=>noticeRow(r)).join('')}`:''}</div></details>`;
    }).join('')||empty(admin?'Thêm tuần học rồi gắn bài học, tài liệu và bài tập vào từng tuần.':'Giảng viên chưa đăng nội dung theo tuần.')}</section>`;
  }
  function shortRow(r,type,admin){
    const action=admin?`data-resource-open="${r.id}" data-resource-kind="${type}"`:`data-learning-detail="${type}" data-item="${r.id}"`;
    return `<div class="cl-resource-row"><i class="fa fa-${type==='material'?'file-text-o':'pencil-square-o'}" aria-hidden="true"></i><button type="button" class="cl-title" ${action}>${esc(r.title)}</button><span class="cl-row-meta">${rowWeeks(r,type)} · ${type==='material'?date(r.created_at):r.practice?'Tự luyện':date(r.due_at)}</span>${type==='assignment'?(badge(r.practice?'Luyện tập':r.practical_id?'Thực hành':'Bài được giao')+badge('Nộp file')):''}</div>`;
  }
  function codeRow(r,admin){
    const type=r.practice?'practice':'practical';
    const open=admin?(r.practice?`data-question-edit="${(r.id.startsWith('practice_')?r.id.slice(9).replace('_'+r.course_id,''):r.id)}"`:`data-practical-open="${r.id}"`):`data-exercise-open="${r.id}"`;
    const status=r.state==='idle'?'Chưa mở':r.state==='ended'?'Đã kết thúc':r.practice?'Tự luyện':'Đang mở';
    return `<div class="cl-resource-row"><i class="fa fa-code" aria-hidden="true"></i><button class="cl-title" type="button" ${open}>${esc(r.title)}</button><span class="cl-row-meta">${label(r.week_number)} · ${r.practice?'Không tính điểm':(r.duration_minutes+' phút')}</span>${badge(names[type])}${badge(status,r.state==='started'?'green':'')}</div>`;
  }
  function resources(data,cid,type,admin){
    bindContext(data,cid,admin);const key=cid+':'+type+':'+admin,s=state(key),c=data.courses.find(c=>c.id===cid);
    const fileRows=(data[type]||[]).filter(r=>r.course_id===cid&&!r.archived);
    const codes=type==='assignments'?(admin?data.code_activities||[]:data.programming?.exams||[]).filter(r=>r.course_id===cid&&r.activity_type&&r.activity_type!=='exam'):[];
    const all=[...fileRows.map(r=>({...r,_type:type==='materials'?'material':'assignment'})),...codes.map(r=>({...r,_type:'code'}))];
    const rows=all.filter(r=>{const placed=assignedWeeks(data,r,r._type);return (!s.q||[r.title,r.description,r.statement,r.original_filename].join(' ').toLocaleLowerCase('vi').includes(s.q.toLocaleLowerCase('vi')))&&(!s.week||(s.week==='0'?!placed.length:placed.includes(Number(s.week))))&&(!s.kind||(r.practice?'practice':r._type==='code'||r.practical_id?'practical':'file')===s.kind);});
    const total=Math.max(1,Math.ceil(rows.length/10));s.page=Math.min(s.page,total);
    return `<section class="panel cl-resource-list" data-cl-list="${esc(key)}" data-cl-type="${type}" data-cl-admin="${admin}"><div class="cl-heading"><div><h2>${type==='materials'?'Tài liệu':'Bài tập'}</h2><p class="muted">Danh sách tổng hợp · Bấm vào tên để xem chi tiết.</p></div>${admin&&c.status!=='completed'?`<button class="btn btn-primary" data-tab="${type==='materials'?'material':'assignment'}">${type==='materials'?'Đăng tài liệu':'Tạo bài nộp file'}</button>`:''}</div><div class="cl-filters"><label>Tìm kiếm<input data-cl-filter="q" value="${esc(s.q)}" placeholder="Tên hoặc nội dung…"></label><label>Tuần học<select data-cl-filter="week">${selectOptions([['','Tất cả tuần'],...weeks(data,cid).map(n=>[n,label(n)]),['0','Chưa gắn tuần']],s.week)}</select></label>${type==='assignments'?`<label>Loại bài<select data-cl-filter="kind">${selectOptions([['','Tất cả'],['file','Bài nộp file thường'],['practice','Luyện tập'],['practical','Thực hành']],s.kind)}</select></label>`:''}</div><div class="cl-lines">${rows.slice((s.page-1)*10,s.page*10).map(r=>r._type==='code'?codeRow(r,admin):shortRow(r,r._type,admin)).join('')||empty('Không có nội dung phù hợp.')}</div><div class="cl-pagination"><span>${rows.length} mục</span><button class="btn btn-ghost" data-cl-page="${s.page-1}" ${s.page<=1?'disabled':''}>Trước</button><span>${s.page}/${total}</span><button class="btn btn-ghost" data-cl-page="${s.page+1}" ${s.page>=total?'disabled':''}>Sau</button></div></section>${type==='assignments'&&admin?management(data,cid):''}`;
  }
  function management(data,cid){
    const c=data.courses.find(c=>c.id===cid),questions=(data.question_bank||[]).filter(q=>q.course_id===cid&&!q.archived),sessions=(data.practicals||[]).filter(r=>r.course_id===cid);
    return `<section class="panel cl-management"><div class="cl-heading"><div><h2>Thực hành theo phiên</h2><p class="muted">Chọn câu trong kho, giao sinh viên và mở giờ chung cho cả lớp.</p></div>${c.status!=='completed'?'<button class="btn btn-primary" data-practical-create>Tạo phiên thực hành</button>':''}</div>${sessions.map(r=>`<div class="cl-resource-row"><i aria-hidden="true" class="fa fa-clock-o"></i><button class="cl-title" data-practical-open="${r.id}">${esc(r.title)}</button><span class="cl-row-meta">${formats[r.response_type]} · ${r.participants.length} sinh viên · ${r.duration_minutes} phút</span>${badge(r.state==='idle'?'Chưa mở':r.state==='started'?'Đang mở':'Đã kết thúc')}${c.status!=='completed'&&r.state!=='ended'?`<button class="btn btn-secondary" data-practical-control="${r.state==='idle'?'start':'end'}" data-id="${r.id}">${r.state==='idle'?'Mở thực hành':'Đóng phiên'}</button>`:''}</div>`).join('')||empty('Chưa có phiên thực hành.')}</section><section class="panel"><div class="cl-heading"><div><h2>Kho bài tập dùng chung</h2><p class="muted">Chọn bài cho sinh viên luyện tập hoặc tạo đề từ cùng một kho. Mỗi bài có thể liên kết nhiều khóa học.</p></div><div class="bridge-inline"><button class="btn btn-primary" data-course-bank>Chọn bài từ kho chung</button><a class="btn btn-secondary" href="/admin/question-bank?course=${cid}">Mở kho bài tập & Đề</a></div></div></section>`;
  }
  function noticeRow(r){return `<div class="cl-resource-row"><i aria-hidden="true" class="fa fa-bullhorn"></i><button class="cl-title" data-course-notice="${r.id}">${esc(r.title)}</button><span class="cl-row-meta">${label(r.week_number)} · ${date(r.starts_at)}</span></div>`;}
  function announcements(data,cid,admin){bindContext(data,cid,admin);return `<section class="panel"><div class="cl-heading"><h2>Thông báo khóa học</h2>${admin?'<button class="btn btn-primary" data-course-notice-create>Đăng thông báo</button>':''}</div>${data.events.filter(r=>r.course_id===cid&&r.kind==='announcement').map(noticeRow).join('')||empty('Chưa có thông báo của khóa học.')}</section>`;}
  function modal(title,body){
    if(context.admin)return window.adminDesign.modal(title,body);
    const d=document.createElement('dialog');d.className='cl-dialog';d.innerHTML=`<div class="cl-heading"><h2>${esc(title)}</h2><button class="btn btn-ghost" data-cl-close aria-label="Đóng">×</button></div>${body}`;document.body.append(d);d.addEventListener('close',()=>d.remove());d.showModal();return d;
  }
  function weekField(value=0){return `<label>Tuần học<input name="week_number" type="number" min="0" max="52" value="${value}"><small>0 = chưa gắn tuần</small></label>`;}
  function checkboxes(rows,name,selected=[]){return rows.map(r=>`<label class="cl-check"><input type="checkbox" name="${name}" value="${r.id}" ${selected.includes(r.id)?'checked':''}>${esc(r.title)}</label>`).join('')||empty('Chưa có nội dung để chọn.');}
  function weekDialog(number){
    const {data,cid}=context,w=(data.course_weeks||[]).find(r=>r.course_id===cid&&String(r.week_number)===number)||{week_number:weeks(data,cid).at(-1)+1||1};
    const rows=key=>data[key].filter(r=>r.course_id===cid&&!r.archived),activities=(data.code_activities||[]).filter(r=>r.course_id===cid);
    const d=modal('Nội dung tuần học',`<form data-cl-form="week" class="stack-form"><input name="course_id" type="hidden" value="${cid}"><label>Tuần số<input name="week_number" type="number" min="1" max="52" value="${w.week_number}" required ${number!=='new'?'readonly':''}></label><label>Tên tuần / chủ đề<input name="title" value="${esc(w.title||'')}" maxlength="200" required></label><label>Bài học<textarea name="lesson_text" rows="5" maxlength="20000">${esc(w.lesson_text||'')}</textarea></label><label>Bài đọc<textarea name="reading_text" rows="4" maxlength="20000">${esc(w.reading_text||'')}</textarea></label><fieldset><legend>Tài liệu</legend>${checkboxes(rows('materials'),'material_ids',w.material_ids)}</fieldset><fieldset><legend>Bài nộp file</legend>${checkboxes(rows('assignments'),'assignment_ids',w.assignment_ids)}</fieldset><fieldset><legend>Bài code</legend>${checkboxes(activities,'activity_ids',w.activity_ids)}</fieldset><fieldset><legend>Thông báo</legend>${checkboxes(rows('events').filter(r=>r.kind==='announcement'),'announcement_ids',w.announcement_ids)}</fieldset><p class="ref-form-error" role="alert"></p><button class="btn btn-primary">Lưu tuần học</button></form>`);
    d.classList.add('cl-dialog');
  }
  function questionDialog(id){
    const {data,cid}=context,q=(data.question_bank||[]).find(r=>r.id===id)||{},kind=q.response_type||'code';
    if(q.published){modal(q.title,`<p class="cl-prose">${esc(q.statement||'')}</p>${(q.programming?.problems||[]).map(p=>`<h3>${esc(p.title)}</h3><p class="cl-prose">${esc(p.statement)}</p><p>${p.tests.length} test · ${p.language||q.programming.languages.join(', ')}</p>`).join('')}<p>Ẩn câu luyện tập trước khi sửa đề để không thay đổi bài đang công bố.</p>`);return;}
    const d=modal(id?'Sửa câu hỏi':'Thêm câu hỏi',`<form data-cl-form="question" class="stack-form"><input type="hidden" name="id" value="${q.id||''}"><input type="hidden" name="course_id" value="${cid}"><label>Tên câu hỏi<input name="title" maxlength="200" value="${esc(q.title||'')}" required></label><div class="cl-filters"><label>Nhóm gợi ý<select name="purpose">${selectOptions(Object.entries(names),q.purpose||'practical')}</select></label><label>Hình thức<select name="response_type" data-question-kind>${selectOptions(Object.entries(formats),kind)}</select></label>${weekField(q.week_number)}</div><label>Nguồn bài<input type="url" name="source_url" value="${esc(q.source_url||'')}" placeholder="https://…"></label><fieldset><legend>Khóa học luyện tập (bỏ trống = chưa gắn khóa nào)</legend>${checkboxes(data.courses.filter(c=>c.status!=='completed').map(c=>({...c,title:c.name})),'course_ids',q.course_ids||[q.course_id||cid])}</fieldset><label>Giới thiệu / Yêu cầu<textarea name="statement" rows="4" maxlength="20000">${esc(q.statement||'')}</textarea></label><div data-file-question ${kind==='file'?'':'hidden'}><label>Định dạng nhận bài<input name="extensions" value="${esc((q.extensions||['.pdf','.txt','.zip']).join(' '))}"></label></div><div data-code-question ${kind==='code'?'':'hidden'}>${window.examConfig.programmingFields(q.programming?q:{programming:{languages:['cpp','java'],problems:[]}})}</div><p class="ref-form-error" role="alert"></p><button class="btn btn-primary">Lưu vào kho chung</button></form>`);
    d.classList.add('cl-dialog','cl-question-dialog');
    window.examConfig.mountProblems();
  }
  function practicalDialog(){
    const {data,cid}=context;
    const d=modal('Tạo phiên thực hành',`<form data-cl-form="practical" class="stack-form"><input type="hidden" name="course_id" value="${cid}"><label>Tên buổi thực hành<input name="title" maxlength="200" required></label><div class="cl-filters"><label>Hình thức<select name="response_type" data-practical-kind>${selectOptions(Object.entries(formats),'code')}</select></label><label>Thời lượng (phút)<input type="number" name="duration_minutes" min="1" max="480" value="60" required></label>${weekField()}</div><label>Mô tả<textarea name="description" maxlength="10000"></textarea></label><label>MSSV được giao<input name="student_ids" placeholder="Để trống để giao cả lớp"><small>Ngăn cách bằng dấu phẩy hoặc khoảng trắng.</small></label><div data-practical-questions></div><p class="muted">Lưu tạo bản nháp riêng tư. Sinh viên chỉ thấy bài sau khi bạn bấm Mở thực hành; cả lớp dùng chung một giờ kết thúc.</p><p class="ref-form-error" role="alert"></p><button class="btn btn-primary">Lưu bản nháp</button></form>`);
    d.classList.add('cl-dialog');updatePracticalChoices(d);
  }
  function updatePracticalChoices(d){const kind=d.querySelector('[data-practical-kind]').value;d.querySelector('[data-practical-questions]').innerHTML=window.questionBank.paperPicker(context.data,{type:kind==='code'?'programming':'file'});}
  function courseBankDialog(){
    const {data,cid}=context,rows=(data.question_bank||[]).filter(q=>q.response_type==='code'&&!q.archived);
    const linked=q=>(q.course_ids||[q.course_id].filter(Boolean)).includes(cid)||!q.explicit_course_links&&!(q.course_ids||[q.course_id].filter(Boolean)).length;
    const d=modal('Chọn bài code từ kho chung',`<p class="muted">Gắn bài vào khóa này. Sinh viên chỉ thấy bài khi giảng viên bật “Cho luyện tập” trong kho; đề thực hành và thi vẫn được chọn riêng.</p><label>Tìm bài<input data-course-bank-search placeholder="Tên bài…"></label><div class="cl-paper-choices">${rows.map(q=>`<label class="cl-check" data-course-bank-row data-search="${esc(q.title.toLocaleLowerCase('vi'))}"><input type="checkbox" data-course-bank-link="${esc(q.id)}" ${linked(q)?'checked':''}> <span>${esc(q.title)} <small>· ${q.published?'Đang cho luyện tập':'Chưa bật luyện tập'}</small></span></label>`).join('')||empty('Kho chưa có bài code.')}</div><p role="alert" class="ref-form-error"></p>`);d.classList.add('cl-dialog');
    let changed=false;d.addEventListener('close',()=>{if(changed)refresh();});
    d.querySelector('[data-course-bank-search]').addEventListener('input',e=>d.querySelectorAll('[data-course-bank-row]').forEach(row=>row.hidden=!row.dataset.search.includes(e.target.value.toLocaleLowerCase('vi'))));
    d.addEventListener('change',async e=>{const input=e.target.closest('[data-course-bank-link]');if(!input)return;input.disabled=true;try{await post('/api/admin/course-questions/link',{id:input.dataset.courseBankLink,target_course_id:cid,enabled:String(input.checked)});const row=rows.find(q=>q.id===input.dataset.courseBankLink);let ids=row.course_ids||[row.course_id].filter(Boolean);if(!ids.length&&!row.explicit_course_links)ids=data.courses.filter(c=>c.status!=='completed').map(c=>c.id);row.course_ids=input.checked?[...new Set([...ids,cid])]:ids.filter(id=>id!==cid);row.explicit_course_links=true;d.querySelector('[role=alert]').textContent='Đã lưu thay đổi.';changed=true;}catch(err){input.checked=!input.checked;d.querySelector('[role=alert]').textContent=err.message;}finally{input.disabled=false;}});
  }
  function resourceDialog(id,kind){
    const {data}=context,r=data[kind==='material'?'materials':'assignments'].find(r=>r.id===id);if(!r)return;
    modal(r.title,`<p class="muted">${label(r.week_number)} · ${date(kind==='material'?r.created_at:r.due_at)}</p><p class="cl-prose">${esc(r.description||'Chưa có mô tả.')}</p>${r.original_filename?`<div class="student-actions"><button class="btn btn-secondary" data-preview-url="/api/learning/preview/${kind==='material'?'materials':'assignments'}/${r.id}">Xem trực tiếp</button><a class="btn btn-secondary" href="/api/learning/files/${kind==='material'?'materials':'assignments'}/${r.id}">Tải ${esc(r.original_filename)}</a></div>`:''}${kind==='assignment'?`<a class="btn btn-primary" href="/admin?section=submissions&course=${context.cid}&activity=assignment%3A${r.id}">Xem các lần nộp & chấm bài</a>`:''}`);
  }
  function assignmentPicker(data){
    const rows=data.courses.filter(c=>data.assignments.some(a=>a.course_id===c.id)||(data.programming?.exams||[]).some(e=>e.course_id===c.id&&e.activity_type!=='exam'));
    return `<section class="panel"><h2>Bài tập theo khóa học</h2><p class="muted">Chọn khóa học để xem bài nộp file, tự luyện và các phiên thực hành được giao.</p><div class="cl-reading">${rows.map(c=>`<article class="panel"><small>${esc(c.code)}</small><h3>${esc(c.name)}</h3><p>${esc(c.semester)}</p><a class="btn btn-primary" href="/student/assignments?course=${c.id}">Mở danh sách bài</a></article>`).join('')||empty('Chưa có bài tập được công bố hoặc giao cho bạn.')}</div></section>`;
  }
  function assignmentCourse(data,c){return `<div class="student-stack"><a href="/student/assignments">← Tất cả khóa học</a><section class="panel"><small>${esc(c.code)}</small><h1>${esc(c.name)}</h1><p class="muted">${esc(c.semester)}</p></section>${resources(data,c.id,'assignments',false)}</div>`;}
  function refresh(){document.dispatchEvent(new Event('course-learning-updated'));}
  async function post(path,body){return window.cssRequest(path,{method:'POST',body:body instanceof FormData?body:new URLSearchParams(body)});}
  document.addEventListener('submit',async event=>{
    const form=event.target.closest('[data-cl-form]');if(!form)return;event.preventDefault();event.stopImmediatePropagation();
    const button=form.querySelector('button[type=submit],button:not([type])');button.disabled=true;
    try{
      const f=new FormData(form),kind=form.dataset.clForm;
      for(const key of ['material_ids','assignment_ids','activity_ids','announcement_ids','question_ids'])if(kind==='week'||key==='question_ids'&&kind==='practical')f.set(key,JSON.stringify(f.getAll(key)));
      if(kind==='question')f.set('course_ids',JSON.stringify(f.getAll('course_ids')));
      if(kind==='practical')f.set('paper_ids',JSON.stringify(f.getAll('paper_ids')));
      if(kind==='question'&&f.get('response_type')==='code'){f.set('languages',f.getAll('language').join(','));f.set('problems',JSON.stringify([...form.querySelectorAll('[data-program-problem]')].map(window.examConfig.captureProblem)));}
      const path={week:'/api/admin/course-content/save',question:'/api/admin/course-questions/save',practical:'/api/admin/course-practicals/save',notice:'/api/learning/event'}[kind];
      if(kind==='notice'){f.set('starts_at',new Date().toISOString());f.set('kind','announcement');}
      await post(path,f);form.closest('dialog').close();window.cssToast('Đã lưu.','success');refresh();
    }catch(e){form.querySelector('[role=alert]').textContent=e.message;}finally{if(button.isConnected)button.disabled=false;}
  },true);
  document.addEventListener('click',async event=>{
    const t=event.target.closest('button');if(!t)return;
    if(!context)return;
    if(t.matches('[data-cl-close]'))t.closest('dialog').close();
    if(t.matches('[data-exercise-run]')){
      const f=t.form,out=f.querySelector('[data-exercise-run-result]');t.disabled=true;out.textContent='Đang chạy test mẫu…';
      try{const result=await post('/api/student/programming/run',{exam_id:f.elements.exam_id.value,problem_index:f.elements.problem_index.value,language:f.elements.language.value,source:f.elements.source.value});out.textContent=result.result.verdict+'\n'+(result.result.compile_log||'')+'\n'+result.result.tests.map(test=>`Test ${test.index}: ${test.verdict}\nOutput: ${test.actual||''}`).join('\n');}catch(e){out.textContent=e.message;}finally{t.disabled=false;}
    }
    if(t.matches('[data-week-edit]'))weekDialog(t.dataset.weekEdit);
    if(t.matches('[data-question-create],[data-question-edit]'))questionDialog(t.dataset.questionEdit);
    if(t.matches('[data-practical-create]'))practicalDialog();
    if(t.matches('[data-course-bank]'))courseBankDialog();
    if(t.matches('[data-resource-open]'))resourceDialog(t.dataset.resourceOpen,t.dataset.resourceKind);
    if(t.matches('[data-course-notice]')){const r=context.data.events.find(r=>r.id===t.dataset.courseNotice);modal(r.title,`<p class="muted">${label(r.week_number)} · ${date(r.starts_at)}</p><p class="cl-prose">${esc(r.description)}</p>`);}
    if(t.matches('[data-course-notice-create]'))modal('Đăng thông báo khóa học',`<form data-cl-form="notice" class="stack-form"><input type="hidden" name="course_id" value="${context.cid}"><label>Tiêu đề<input name="title" required maxlength="200"></label>${weekField()}<label>Nội dung<textarea name="description" required maxlength="10000"></textarea></label><p class="ref-form-error" role="alert"></p><button class="btn btn-primary">Đăng thông báo</button></form>`);
    if(t.matches('[data-cl-page]')){state(t.closest('[data-cl-list]').dataset.clList).page=Number(t.dataset.clPage);refreshList(t.closest('[data-cl-list]'));}
    if(t.matches('[data-question-control],[data-practical-control]')){
      t.disabled=true;try{await post(`/api/admin/${t.dataset.questionControl?'course-questions/'+t.dataset.questionControl:'course-practicals/'+t.dataset.practicalControl}`,{id:t.dataset.id});refresh();}catch(e){window.cssToast(e.message,'error');t.disabled=false;}
    }
    if(t.matches('[data-exercise-open]')){
      const row=context.data.programming.exams.find(r=>r.id===t.dataset.exerciseOpen);t.disabled=true;
      try{if(!row.attempt){if(!row.can_start)throw new Error('Phiên chưa mở hoặc đã hết giờ.');await post('/api/student/programming/start',{exam_id:row.id});}location.assign('/student/exams?exam='+encodeURIComponent(row.id)+(row.problems?.length?'&problem='+row.problems[0].index:''));}catch(e){window.cssToast(e.message,'error');t.disabled=false;}
    }
    if(t.matches('[data-practical-open]')){
      const r=(context.data.practicals||[]).find(r=>r.id===t.dataset.practicalOpen);if(!r)return;
      modal(r.title,`<p>${formats[r.response_type]} · ${r.duration_minutes} phút · ${r.participants.length} sinh viên</p><p class="cl-prose">${esc(r.description||'')}</p><p>Mở: ${date(r.started_at)} · Đóng: ${date(r.ends_at)}</p><p>${r.question_ids.length} câu hỏi được chụp lại khi tạo phiên.</p><a class="btn btn-primary" href="/admin?section=submissions&course=${context.cid}">Xem lịch sử bài nộp</a>`);
    }
  });
  function refreshList(node,focused){
    const scratch=document.createElement('div');scratch.innerHTML=resources(context.data,context.cid,node.dataset.clType,node.dataset.clAdmin==='true');const replacement=scratch.querySelector('[data-cl-list]');node.replaceWith(replacement);
    if(focused){const input=replacement.querySelector(`[data-cl-filter="${focused.name}"]`);input?.focus();if(input?.setSelectionRange&&input.type==='text')input.setSelectionRange(focused.position,focused.position);}
  }
  function listFilter(event){const input=event.target.closest('[data-cl-filter]');if(!input)return;const list=input.closest('[data-cl-list]'),s=state(list.dataset.clList);s[input.dataset.clFilter]=input.value;s.page=1;refreshList(list,{name:input.dataset.clFilter,position:input.selectionStart});}
  document.addEventListener('input',event=>{if(event.target.matches('[data-cl-filter=q]'))listFilter(event);filterBank(event);});
  document.addEventListener('change',event=>{
    if(event.target.matches('select[data-cl-filter]'))listFilter(event);
    if(event.target.matches('[data-question-kind]')){const f=event.target.form,isCode=event.target.value==='code';f.querySelector('[data-code-question]').hidden=!isCode;f.querySelector('[data-file-question]').hidden=isCode;f.querySelectorAll('[data-code-question] input,[data-code-question] textarea,[data-code-question] select').forEach(el=>el.disabled=!isCode);}
    if(event.target.matches('[data-practical-kind]'))updatePracticalChoices(event.target.closest('dialog'));
    filterBank(event);
  });
  function filterBank(event){if(!event.target.matches('[data-bank-search],[data-bank-purpose],[data-bank-format]'))return;const panel=event.target.closest('.panel'),q=panel.querySelector('[data-bank-search]').value.toLocaleLowerCase('vi'),purpose=panel.querySelector('[data-bank-purpose]').value,format=panel.querySelector('[data-bank-format]').value;panel.querySelectorAll('[data-bank-row]').forEach(row=>row.hidden=(!row.dataset.search.includes(q))||(purpose&&row.dataset.purpose!==purpose)||(format&&row.dataset.format!==format));}
  window.courseLearning={editQuestion:questionDialog,modal,weekly,resources,announcements,weekField,assignmentPicker,assignmentCourse,setContext:bindContext};
})();
