/* Shared taxonomy controls and the role/course administration page. */
(() => {
  'use strict';
  const esc=window.cssEscape,filters=new Map(),listeners=[];
  let catalog={topics:[],difficulties:{easy:'Dễ',medium:'Trung bình',hard:'Khó'},languages:{c:'C',cpp:'C++',java:'Java',python:'Python'}},pageData=null;
  const assignmentDrafts=new Map();
  let bankSearch="";
  const role=()=>document.querySelector('[data-user-role]')?.dataset.userRole;
  const options=(items,selected)=>items.map(([id,label])=>`<option value="${esc(id)}" ${selected.includes(id)?'selected':''}>${esc(label)}</option>`).join('');
  function fields(row={}){
    const topics=catalog.topics.filter(t=>t.active!==false||(row.topic_ids||[]).includes(t.id));
    return `<fieldset class="classification-fields"><legend>Phân loại nội dung</legend><div class="two-cols"><label>Chủ đề (có thể chọn nhiều)<select name="topic_ids_choice" multiple size="4">${options(topics.map(t=>[t.id,t.name+(t.active===false?' · ngừng sử dụng':'')]),row.topic_ids||[])}</select></label><label>Độ khó chính<select name="difficulty">${options(Object.entries(catalog.difficulties),[row.difficulty||'medium'])}</select></label><label>Ngôn ngữ phân loại<select name="classification_language_choice" multiple size="4">${options(Object.entries(catalog.languages),row.classification_languages||[])}</select></label></div><p class="muted">Giữ Ctrl/Cmd để chọn nhiều chủ đề hoặc ngôn ngữ. Ngôn ngữ chạy code vẫn theo cấu hình bộ chấm của nội dung.</p></fieldset>`;
  }
  function payload(form,body){
    if(!form.querySelector('[name=topic_ids_choice]'))return body;
    body.set('topic_ids',JSON.stringify([...form.elements.topic_ids_choice.selectedOptions].map(o=>o.value)));
    body.set('difficulty',form.elements.difficulty.value);
    body.set('classification_languages',JSON.stringify([...form.elements.classification_language_choice.selectedOptions].map(o=>o.value)));
    return body;
  }
  function badges(row){
    return `<span class="classification-badges">${(row.topic_ids||[]).map(id=>`<span class="bridge-pill">${esc(catalog.topics.find(t=>t.id===id)?.name||'Chủ đề đã lưu')}</span>`).join('')}${row.difficulty?`<span class="bridge-pill">${esc(catalog.difficulties[row.difficulty]||row.difficulty)}</span>`:''}${(row.classification_languages||[]).map(l=>`<span class="bridge-pill">${esc(catalog.languages[l]||l)}</span>`).join('')}</span>`;
  }
  function filter(items,id){
    const state=filters.get(id)||{},kind=r=>r.content_type||(r.programming_homework||r.activity_type==='assignment'?'assignment':r.type?'exam':'file_assignment');
    const select=(name,label,items)=>`<label>${label}<select data-classification-filter="${esc(id)}" data-criterion="${name}"><option value="">Tất cả</option>${options(items,[state[name]||''])}</select></label>`;
    const controls=`<div class="classification-filters">${select('topic','Chủ đề',catalog.topics.map(t=>[t.id,t.name]))}${select('difficulty','Độ khó',Object.entries(catalog.difficulties))}${select('language','Ngôn ngữ',Object.entries(catalog.languages))}${select('kind','Loại nội dung',[['assignment','Bài tập lập trình'],['file_assignment','Bài tập nộp file'],['exam','Đề thi'],['question','Câu hỏi']])}</div>`;
    return {controls,items:items.filter(r=>(!state.topic||(r.topic_ids||[]).includes(state.topic))&&(!state.difficulty||r.difficulty===state.difficulty)&&(!state.language||(r.classification_languages?.length?r.classification_languages:r.programming?.languages||r.languages||[]).includes(state.language))&&(!state.kind||kind(r)===state.kind))};
  }
  document.addEventListener('change',event=>{
    if(event.target.matches?.('[name=target_type],[name=target_id]')){const form=event.target.form,input=form.querySelector('[data-reuse-due]');if(input){input.required=form.elements.target_type.value==='assignment'&&!form.elements.target_id.value;input.disabled=!input.required;}return;}
    if(event.target.matches?.('[name=teacher_choice]')){
      const form=event.target.form,ids=[...form.querySelectorAll('[name=teacher_choice]:checked')].map(input=>input.value);
      assignmentDrafts.set(form.elements.course_id.value,ids);
      form.querySelector('[data-assignment-selection]').textContent=`Đang chọn ${ids.length} giáo viên · Chưa lưu`;
      return;
    }
    const select=event.target.closest('[data-classification-filter]');if(!select)return;
    const id=select.dataset.classificationFilter,state=filters.get(id)||{};state[select.dataset.criterion]=select.value;filters.set(id,state);
    listeners.forEach(fn=>fn());
    if(document.getElementById('classification-page'))draw();
  });
  async function loadPage(){
    pageData=await window.cssRequest('/api/admin/classification');catalog={...catalog,...pageData};draw();
  }
  function bank(){return window.questionLibraryUI.bank(pageData,{filter,badges,search:bankSearch});}
  function draw(){
    const root=document.getElementById('classification-page');if(!root||!pageData)return;
    const admin=role()==='admin',view=filter(pageData.content,'classification:content');
    root.innerHTML=`<section class="panel"><h1>Phân loại & phân quyền</h1><p>Danh mục chung toàn hệ thống. Giáo viên chỉ quản lý nội dung mình tạo trong khóa học được phân công.</p><h2>Chủ đề</h2>${admin?'<form class="stack-form" data-tax-action="topics/save"><label>Tên chủ đề<input name="name" maxlength="120" required></label><button class="btn btn-primary">Thêm chủ đề</button></form>':''}<div class="resource-lines">${pageData.topics.map(t=>`<div class="student-row"><strong>${esc(t.name)}</strong><span>${t.active===false?'Ngừng sử dụng':'Đang sử dụng'}</span>${admin?`<button type="button" class="btn btn-secondary" data-topic-edit="${t.id}">Đổi tên</button>${t.active===false?'':`<button type="button" class="btn btn-ghost" data-tax-post="topics/archive" data-item-id="${t.id}">Ngừng sử dụng</button>`}`:''}</div>`).join('')||'<p>Chưa có chủ đề.</p>'}</div></section>${admin?adminFields():''}${bank()}<section class="panel"><div class="ref-heading-row"><h2>Phân loại nội dung thuộc quyền quản lý</h2><button type="button" class="btn btn-primary" data-question-create>Tạo câu hỏi lập trình</button></div>${view.controls}<div class="resource-lines">${view.items.map(row=>`<details class="resource-line"><summary><span class="resource-line-title">${esc(row.title)}</span><span>${esc(({assignment:'Bài lập trình',exam:'Đề thi',question:'Câu hỏi'})[row.content_type])}</span></summary><div class="resource-line-body">${badges(row)}<p>Người tạo: ${esc(row.created_by||'Nội dung cũ do Admin quản lý')}</p><form class="stack-form" data-tax-action="classification/assign"><input type="hidden" name="id" value="${row.id}"><input type="hidden" name="content_type" value="${row.content_type}">${fields(row)}${row.content_type==='question'?window.questionLibraryUI.purposeField(row):''}<button class="btn btn-primary">Lưu phân loại</button></form>${row.content_type==='question'?`<div class="ref-actions">${!row.published?`<button type="button" class="btn btn-secondary" data-question-edit="${row.id}">Sửa câu hỏi</button><button type="button" class="btn btn-primary" data-tax-post="questions/publish" data-item-id="${row.id}">Công bố câu hỏi</button>`:'<span>Đã công bố</span>'}<button type="button" class="btn btn-ghost" data-tax-post="questions/archive" data-item-id="${row.id}">Lưu trữ câu hỏi</button></div>`:''}</div></details>`).join('')||'<p>Chưa có nội dung phù hợp.</p>'}</div></section>`;
  }
  function assignmentFields(course,teachers){
    const selected=assignmentDrafts.get(course.id)||course.teacher_ids;
    const saved=course.teacher_ids.map(id=>teachers.find(t=>t.id===id)?.full_name+' ('+id+')').join(', ');
    return `<form class="stack-form course-teacher-assignment" data-tax-action="courses/teachers"><input type="hidden" name="course_id" value="${course.id}"><h3>${esc(course.name)}</h3><p class="muted" data-assignment-saved>Đang phụ trách: ${saved?esc(saved):'Chưa phân công giáo viên'}</p><fieldset><legend>Chọn giáo viên phụ trách</legend>${teachers.map(t=>`<label class="teacher-assignment-option"><input type="checkbox" name="teacher_choice" value="${esc(t.id)}" ${selected.includes(t.id)?'checked':''} ${!t.active&&!selected.includes(t.id)?'disabled':''}><span><strong>${esc(t.full_name)}</strong><small>${esc(t.id)}${t.active?'':' · Đã khóa'}</small></span></label>`).join('')||'<p class="muted">Hãy tạo tài khoản Giáo viên trước.</p>'}</fieldset><p class="muted" data-assignment-selection>Đang chọn ${selected.length} giáo viên${assignmentDrafts.has(course.id)?' · Chưa lưu':''}</p><button class="btn btn-primary" ${teachers.length?'':'disabled'}>Lưu phân công</button></form>`;
  }
  function adminFields(){
    const teachers=pageData.teachers||[];
    return `<section class="panel"><h2>Tài khoản Giáo viên</h2><form class="stack-form" data-tax-action="teachers/save"><div class="two-cols"><label>Tên tài khoản<input name="id" required maxlength="80"></label><label>Họ tên<input name="full_name" required maxlength="200"></label><label>Mật khẩu (để trống khi chỉ sửa thông tin)<input name="password" type="password" autocomplete="new-password"></label><label>Trạng thái<select name="active"><option value="true">Hoạt động</option><option value="false">Khóa</option></select></label></div><button class="btn btn-primary">Tạo / cập nhật Giáo viên</button></form><ul>${teachers.map(t=>`<li>${esc(t.id)} · ${esc(t.full_name)} · ${t.active?'Hoạt động':'Đã khóa'}</li>`).join('')}</ul></section><section class="panel"><h2>Phân công khóa học</h2>${pageData.courses.map(c=>assignmentFields(c,teachers)).join('')}</section>`;
  }
  document.addEventListener('submit',async event=>{
    const form=event.target;
    if(form.matches('[data-bank-search]')){event.preventDefault();event.stopImmediatePropagation();bankSearch=form.elements.query.value;draw();document.getElementById('question-bank').scrollIntoView({block:'start'});return;}if(!form.matches('[data-tax-action]'))return;
    event.preventDefault();event.stopImmediatePropagation();if(form.dataset.saving)return;
    form.dataset.saving='true';
    try{
      const body=payload(form,new FormData(form));
      if(form.dataset.taxAction==='courses/teachers'){
        const ids=[...form.querySelectorAll('[name=teacher_choice]:checked')].map(input=>input.value);
        const current=pageData.courses.find(c=>c.id===form.elements.course_id.value);
        if(!ids.length&&!current.teacher_ids.length)throw new Error('Chưa chọn giáo viên. Hãy tích vào ô trước tên giáo viên rồi bấm Lưu phân công.');
        if(!ids.length&&!confirm('Bỏ toàn bộ giáo viên phụ trách khóa học này?'))return;
        body.set('teacher_ids',JSON.stringify(ids));
      }
      if(form.dataset.taxAction==='questions/save'&&form.elements.response_type?.value!=='file'){
        const config=window.examConfig.payload(form);for(const key of ['languages','problems'])body.set(key,config.get(key));
      }
      if(['questions/reuse','questions/assign-files'].includes(form.dataset.taxAction)&&body.get('due_at'))body.set('due_at',new Date(body.get('due_at')+'+07:00').toISOString());
      const result=await window.cssRequest('/api/admin/'+form.dataset.taxAction,{method:'POST',body});
      if(form.dataset.taxAction==='questions/reuse'){form.closest('dialog')?.close();await loadPage();window.cssToast('Đã lưu bản nháp. Mở Khóa học hoặc Cấu hình kỳ thi để chỉnh sửa và giao bài.','success');return;}
      if(form.dataset.taxAction==='questions/assign-files'&&!document.getElementById('classification-page')){location.reload();return;}
      if(form.dataset.taxAction==='courses/teachers'){
        const next=await window.cssRequest('/api/admin/classification'),course=next.courses.find(c=>c.id===form.elements.course_id.value);
        const expected=JSON.parse(body.get('teacher_ids')).sort();
        if(!course||JSON.stringify([...course.teacher_ids].sort())!==JSON.stringify(expected))throw new Error('Dữ liệu phân công chưa được lưu đúng. Hãy tải lại trang và kiểm tra.');
        assignmentDrafts.delete(course.id);pageData=next;catalog={...catalog,...next};draw();
        window.cssToast(`Đã lưu phân công ${expected.length} giáo viên cho khóa học.`,'success');
      }else{form.closest('dialog')?.close();await loadPage();window.cssToast('Đã lưu.','success');}
    }catch(error){window.cssToast(error.message,'error');window.adminDesign.formError(form,error.message);}
    finally{delete form.dataset.saving;}
  },true);
  document.addEventListener('click',async event=>{
    const edit=event.target.closest('[data-topic-edit]');if(edit){
      const row=pageData.topics.find(t=>t.id===edit.dataset.topicEdit);
      window.adminDesign.modal('Đổi tên chủ đề',`<form class="stack-form" data-tax-action="topics/save"><input type="hidden" name="id" value="${row.id}"><label>Tên chủ đề<input name="name" value="${esc(row.name)}" maxlength="120" required></label><button class="btn btn-primary">Lưu</button></form>`);return;
    }
    const post=event.target.closest('[data-tax-post]');if(post){
      try{await window.cssRequest('/api/admin/'+post.dataset.taxPost,{method:'POST',body:new URLSearchParams({id:post.dataset.itemId})});await loadPage();}catch(error){window.cssToast(error.message,'error');}return;
    }
    const reuse=event.target.closest('[data-question-reuse]');if(reuse){
      const row=pageData.content.find(r=>r.id===reuse.dataset.questionReuse);
      window.adminDesign.modal('Tái sử dụng câu hỏi',`<form class="stack-form" data-tax-action="questions/reuse"><input type="hidden" name="id" value="${row.id}"><label>Tạo nội dung<select name="target_type"><option value="assignment">Bài tập lập trình (bản nháp)</option><option value="exam">Đề thi lập trình (bản nháp)</option><option value="question">Phiên bản câu hỏi mới</option></select></label><label>Khóa học<select name="course_id" required>${options(pageData.courses.map(c=>[c.id,c.name]),[row.course_id])}</select></label><label>Nội dung đích<select name="target_id"><option value="">Tạo bản nháp mới</option>${options(pageData.content.filter(r=>['assignment','exam'].includes(r.content_type)&&r.state==='idle'&&r.programming).map(r=>[r.id,`${r.content_type==='exam'?'Đề thi':'Bài tập'} · ${r.title}`]),[])}</select></label><p class="muted">Khi thêm vào bản nháp có sẵn, chọn đúng loại nội dung và khóa học tương ứng. Ngôn ngữ chạy sẽ lấy phần chung của các câu hỏi.</p><label>Tiêu đề bài tập / đề thi<input name="title" value="${esc(row.title)}" required maxlength="200"></label><label>Hạn nộp bài tập (giờ Việt Nam)<input type="datetime-local" name="due_at" data-reuse-due required></label><label>Thời lượng đề thi (phút)<input type="number" name="duration_minutes" min="1" max="1440" value="90"></label><p class="muted">Sao chép đề bài, điểm, giới hạn chạy, test case và phân loại. Chủ đề đã ngừng sử dụng không được gán cho bản mới. Bản sao có thể sửa độc lập.</p><button class="btn btn-primary">Lưu bản nháp</button></form>`);return;
    }
    const question=event.target.closest('[data-question-create],[data-question-edit]');if(!question)return;
    const row=pageData.content.find(r=>r.id===question.dataset.questionEdit)||{};
    const dialog=window.adminDesign.modal('Câu hỏi lập trình',`<form class="stack-form" data-tax-action="questions/save"><input type="hidden" name="id" value="${row.id||''}"><input type="hidden" name="type" value="programming"><label>Khóa học<select name="course_id" required>${options(pageData.courses.map(c=>[c.id,c.name]),[row.course_id||pageData.courses[0]?.id])}</select></label>${fields(row)}${window.examConfig.programmingFields(row)}<p class="muted">Mỗi câu hỏi cần đúng một bài toán và ít nhất một test case. Câu hỏi chưa tự giao cho học viên.</p><button class="btn btn-primary">Lưu câu hỏi</button></form>`);
    window.examConfig.showProblem(dialog.querySelector('[data-program-problem]'));
  });
  addEventListener('DOMContentLoaded',()=>{if(document.getElementById('classification-page'))loadPage().catch(e=>window.cssToast(e.message,'error'));});
  window.classificationUI={redraw:draw,fields,payload,badges,filter,setCatalog(value){if(value)catalog={...catalog,...value};},onChange(fn){listeners.push(fn);}};
})();
