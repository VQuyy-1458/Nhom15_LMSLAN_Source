/* Purposes, file/code question editors and reusable paper management. */
(() => {
  'use strict';
  const esc=window.cssEscape;
  let context=null,purpose='',format='';
  const purposes={practice:'Luyện tập',practical:'Thực hành',exam:'Thi'},formats={code:'Code',file:'Nộp file'};
  const options=(rows,value)=>rows.map(([id,label])=>`<option value="${esc(id)}" ${id===value?'selected':''}>${esc(label)}</option>`).join('');
  const courseOptions=value=>options(context.courses.map(c=>[c.id,c.name]),value||context.courses[0]?.id);
  const cloneButton=q=>`<button type="button" class="btn btn-secondary" data-tax-post="questions/clone" data-item-id="${q.id}">Tạo phiên bản mới</button>`;
  function bank(data,helpers){
    context=data;
    const view=helpers.filter(data.content.filter(r=>r.content_type==='question'),'classification:bank');
    const query=(helpers.search||'').trim().toLocaleLowerCase('vi');
    const rows=view.items.filter(q=>(!purpose||(q.purpose||'exam')===purpose)&&(!format||(q.response_type||'code')===format)&&[q.title,q.id,q.file_question?.statement,q.programming?.problems?.[0]?.statement,...(q.topic_ids||[]).map(id=>data.topics.find(t=>t.id===id)?.name||'')].join(' ').toLocaleLowerCase('vi').includes(query));
    return `<section class="panel" id="question-bank"><div class="ref-heading-row"><h2>Ngân hàng câu hỏi</h2><button type="button" class="btn btn-primary" data-question-create>Tạo câu hỏi</button></div><p>Câu luyện tập đã công bố được sinh viên trong lớp tự tiếp cận. Câu thực hành và thi chỉ hiện sau khi được giao.</p><form data-bank-search class="stack-form"><label>Tìm tên, mã, nội dung hoặc chủ đề<input name="query" value="${esc(helpers.search||'')}" maxlength="200"></label><button class="btn btn-secondary">Tìm kiếm</button></form><div class="two-cols"><label>Mục đích<select data-library-purpose><option value="">Tất cả</option>${options(Object.entries(purposes),purpose)}</select></label><label>Hình thức<select data-library-format><option value="">Tất cả</option>${options(Object.entries(formats),format)}</select></label></div>${view.controls}<p>${rows.length} câu hỏi phù hợp</p><div class="resource-lines">${rows.map(q=>{
      const code=q.response_type!=='file',p=code?q.programming.problems[0]:q.file_question;
      return `<details class="resource-line"><summary><span class="resource-line-title">${esc(q.title)}</span><span>${purposes[q.purpose||'exam']} · ${code?'Code':'Nộp file'} · ${q.published?'Đã công bố':'Bản nháp'}</span></summary><div class="resource-line-body">${helpers.badges(q)}<p>Mã: ${esc(q.id)} · ${esc(data.courses.find(c=>c.id===q.course_id)?.name||'')}</p><p class="student-description">${esc(p.statement||'Chưa có mô tả.')}</p><p>${p.points} điểm ${code?`· ${q.programming.languages.map(esc).join(', ')} · ${p.tests.length} test case`:`· ${p.extensions.map(esc).join(', ')}`}</p>${code?`<details><summary>Xem test case (dành cho người quản lý)</summary>${p.tests.map((t,i)=>`<strong>Test ${i+1} · ${t.sample?'Mẫu':'Ẩn'}</strong><p>Input</p><pre>${esc(t.input)}</pre><p>Output</p><pre>${esc(t.output)}</pre>`).join('')}</details>`:''}<div class="ref-actions">${!q.published?`<button type="button" class="btn btn-secondary" data-question-edit="${q.id}">Sửa câu hỏi</button><button type="button" class="btn btn-primary" data-tax-post="questions/publish" data-item-id="${q.id}">Công bố câu hỏi</button>`:''}${code?`<button type="button" class="btn btn-primary" data-question-reuse="${q.id}">Tái sử dụng / Tạo phiên bản</button>`:`<button type="button" class="btn btn-primary" data-library-file-assign="${q.id}">Giao bài thực hành</button>`}${cloneButton(q)}<button type="button" class="btn btn-ghost" data-tax-post="questions/archive" data-item-id="${q.id}">Lưu trữ câu hỏi</button></div></div></details>`;
    }).join('')||'<p>Chưa có câu hỏi phù hợp.</p>'}</div></section>${papers(data)}`;
  }
  function papers(data){
    return `<section class="panel" id="paper-library"><div class="ref-heading-row"><h2>Đề thi độc lập</h2><button type="button" class="btn btn-primary" data-paper-create>Tạo đề từ ngân hàng</button></div><p>Một đề gồm nhiều câu hỏi và điểm, được lưu riêng để sử dụng trong nhiều kỳ thi có lịch và danh sách sinh viên khác nhau.</p>${(data.papers||[]).map(p=>`<details class="resource-line"><summary><span class="resource-line-title">${esc(p.title)}</span><span>${formats[p.response_type]} · ${p.question_ids.length} câu · ${p.published?'Đã công bố':'Bản nháp'}</span></summary><div class="resource-line-body"><p>${(p.programming?.problems||p.file_questions||[]).map(q=>esc(q.title)).join(' · ')}</p><div class="ref-actions">${!p.published?`<button type="button" class="btn btn-secondary" data-paper-edit="${p.id}">Sửa đề</button><button type="button" class="btn btn-primary" data-tax-post="papers/publish" data-item-id="${p.id}">Công bố đề</button>`:''}<button type="button" class="btn btn-secondary" data-tax-post="papers/clone" data-item-id="${p.id}">Tạo bản sao</button><button type="button" class="btn btn-ghost" data-tax-post="papers/archive" data-item-id="${p.id}">Lưu trữ</button></div></div></details>`).join('')||'<p>Chưa có đề thi độc lập.</p>'}</section>`;
  }
  function toggleQuestion(form){
    const file=form.elements.response_type.value==='file';
    for(const [selector,disabled] of [['[data-library-code]',file],['[data-library-file]',!file]]){
      const node=form.querySelector(selector);node.hidden=disabled;node.disabled=disabled;
    }
  }
  document.addEventListener('click',event=>{
    const practical=event.target.closest('[data-library-practical]');if(practical){void fileAssignment(practical.dataset.libraryPractical);return;}
    const question=event.target.closest('[data-question-create],[data-question-edit]');
    if(question&&context){
      event.preventDefault();event.stopImmediatePropagation();
      const q=context.content.find(r=>r.id===question.dataset.questionEdit)||{},f=q.file_question||{};
      const dialog=window.adminDesign.modal('Câu hỏi trong ngân hàng',`<form class="stack-form" data-tax-action="questions/save"><input type="hidden" name="id" value="${q.id||''}"><input type="hidden" name="type" value="programming"><label>Khóa học<select name="course_id" required>${courseOptions(q.course_id)}</select></label><div class="two-cols"><label>Mục đích<select name="purpose">${options(Object.entries(purposes),q.purpose||'exam')}</select></label><label>Hình thức<select name="response_type">${options(Object.entries(formats),q.response_type||'code')}</select></label></div>${window.classificationUI.fields(q)}<fieldset data-library-code>${window.examConfig.programmingFields(q)}</fieldset><fieldset data-library-file><label>Tên câu hỏi<input name="file_title" required maxlength="200" value="${esc(q.response_type==='file'?q.title:'')}"></label><label>Đề bài / Yêu cầu bài nộp<textarea name="file_statement" required maxlength="20000" rows="6">${esc(f.statement||'')}</textarea></label><label>Điểm<input type="number" name="file_points" min="1" max="1000" value="${f.points||100}"></label><label>Định dạng bài nộp<input name="file_extensions" required value="${esc((f.extensions||['.pdf','.zip','.txt']).join(' '))}"></label></fieldset><p class="muted">Code cần đúng một bài toán và ít nhất một test case. Nộp file được giảng viên chấm và phản hồi.</p><button class="btn btn-primary">Lưu câu hỏi</button></form>`);
      toggleQuestion(dialog.querySelector('form'));window.examConfig.showProblem(dialog.querySelector('[data-program-problem]'));return;
    }
    const paper=event.target.closest('[data-paper-create],[data-paper-edit]');
    if(paper&&context){
      const p=context.papers.find(r=>r.id===paper.dataset.paperEdit)||{};
      const dialog=window.adminDesign.modal('Đề thi độc lập',`<form class="stack-form" data-tax-action="papers/save"><input type="hidden" name="id" value="${p.id||''}"><input type="hidden" name="question_ids" value="[]"><label>Tên đề thi<input name="title" value="${esc(p.title||'')}" required maxlength="200"></label><label>Khóa học<select name="course_id">${courseOptions(p.course_id)}</select></label><label>Hình thức<select name="response_type">${options(Object.entries(formats),p.response_type||'code')}</select></label><div class="exam-bank-list">${context.content.filter(q=>q.content_type==='question').map(q=>`<label class="teacher-assignment-option" data-paper-row data-format="${q.response_type||'code'}"><input type="checkbox" data-paper-question value="${q.id}" ${(p.question_ids||[]).includes(q.id)?'checked':''}><span>${esc(q.title)} · ${purposes[q.purpose||'exam']}</span></label>`).join('')}</div><button class="btn btn-primary">Lưu đề thi</button></form>`);
      syncPaper(dialog.querySelector('form'));return;
    }
    const file=event.target.closest('[data-library-file-assign]');if(file){
      const q=context.content.find(r=>r.id===file.dataset.libraryFileAssign);
      window.adminDesign.modal('Giao bài thực hành nộp file',`<form class="stack-form" data-tax-action="questions/assign-files"><input type="hidden" name="question_ids" value='${esc(JSON.stringify([q.id]))}'><label>Tên bài<input name="title" value="${esc(q.title)}" required></label><label>Khóa học<select name="course_id">${courseOptions(q.course_id)}</select></label><label>Hạn nộp (giờ Việt Nam)<input type="datetime-local" name="due_at" required></label><button class="btn btn-primary">Giao cho lớp</button></form>`);
    }
  },true);
  function syncPaper(form){
    form.querySelectorAll('[data-paper-row]').forEach(row=>{row.hidden=row.dataset.format!==form.elements.response_type.value;row.querySelector('input').disabled=row.hidden;});
    form.elements.question_ids.value=JSON.stringify([...form.querySelectorAll('[data-paper-question]:checked:not(:disabled)')].map(n=>n.value));
  }
  async function fileAssignment(course){
    try{
      const data=await window.cssRequest('/api/admin/classification');context=data;
      const questions=data.content.filter(q=>q.content_type==='question'&&q.response_type==='file');
      window.adminDesign.modal('Tạo bài thực hành nộp file từ ngân hàng',`<form class="stack-form" data-tax-action="questions/assign-files"><input type="hidden" name="question_ids" value="[]"><input type="hidden" name="course_id" value="${esc(course)}"><label>Tên bài thực hành<input name="title" required maxlength="200"></label><label>Hạn nộp (giờ Việt Nam)<input type="datetime-local" name="due_at" required></label><div class="exam-bank-list">${questions.map(q=>`<label class="teacher-assignment-option"><input type="checkbox" data-file-practical-question value="${q.id}"><span>${esc(q.title)} · ${purposes[q.purpose||'exam']}</span></label>`).join('')||'<p>Chưa có câu hỏi nộp file.</p>'}</div><button class="btn btn-primary">Tạo & giao cho lớp</button></form>`);
    }catch(error){window.cssToast(error.message,'error');}
  }
  document.addEventListener('change',event=>{
    const form=event.target.form;
    if(form?.dataset.taxAction==='questions/save'&&event.target.name==='response_type')toggleQuestion(form);
    if(form?.dataset.taxAction==='papers/save')syncPaper(form);
    if(form?.dataset.taxAction==='questions/assign-files'&&event.target.matches('[data-file-practical-question]'))form.elements.question_ids.value=JSON.stringify([...form.querySelectorAll('[data-file-practical-question]:checked')].map(n=>n.value));
    if(event.target.matches('[data-library-purpose],[data-library-format]')){
      if(event.target.matches('[data-library-purpose]'))purpose=event.target.value;else format=event.target.value;
      window.classificationUI.redraw();
    }
  });
  window.questionLibraryUI={bank,purposeField:q=>`<label>Mục đích sử dụng<select name="purpose">${options(Object.entries(purposes),q.purpose||'exam')}</select></label>`,practicalButton:course=>`<button type="button" class="btn btn-secondary" data-library-practical="${esc(course)}">Chọn câu nộp file từ ngân hàng</button>`};
})();
