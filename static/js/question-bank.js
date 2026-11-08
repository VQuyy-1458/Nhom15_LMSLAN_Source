(() => {
  'use strict';
  const esc=window.cssEscape;
  const category={practice:'Luyện tập',lab:'Thực hành',exam:'Thi'};
  const kind={code:'Nộp code',file:'Nộp file'};
  let editor='';
  let selectedKind='code';
  const byCourse=(data,c)=>data.questions.filter(q=>q.course_id===c.id);
  function view(data,c){
    const questions=byCourse(data,c),papers=data.papers.filter(p=>p.course_id===c.id);
    const active=questions.find(q=>q.id===editor);
    const problem=active?.problem||{};
    return `<section class="panel"><div class="panel-heading"><div><h2>Ngân hàng câu hỏi</h2><p class="muted">Câu hỏi được lưu độc lập, dùng lại cho bài tập hoặc đề thi. Câu luyện tập chỉ hiện với sinh viên khi bật công khai.</p></div><button type="button" class="btn btn-primary" data-question-new>+ Tạo câu hỏi</button></div><div class="student-admin-list">${questions.map(q=>`<div class="student-row"><div class="student-row-body"><strong>${esc(q.problem.title)}</strong><p class="muted">${category[q.category]} · ${kind[q.kind]}${q.published?' · Đã công khai':''} · ${q.problem.tests?.length||0} test</p></div><button type="button" class="btn btn-secondary" data-question-edit="${q.id}">Cấu hình</button></div>`).join('')||'<p class="muted">Chưa có câu hỏi trong khóa học.</p>'}</div></section>${editor!==''?`<section class="panel"><h2>${active?'Sửa câu hỏi':'Tạo câu hỏi'}</h2><form class="stack-form" data-question-form><input type="hidden" name="id" value="${esc(active?.id||'')}"><input type="hidden" name="course_id" value="${esc(c.id)}"><div class="two-cols"><label>Phân loại<select name="category"><option value="practice" ${active?.category==='practice'?'selected':''}>Luyện tập</option><option value="lab" ${active?.category==='lab'?'selected':''}>Thực hành</option><option value="exam" ${active?.category==='exam'?'selected':''}>Thi</option></select></label><label>Hình thức<select name="kind"><option value="code" ${selectedKind==='code'?'selected':''}>Nộp code</option><option value="file" ${selectedKind==='file'?'selected':''}>Nộp file</option></select></label></div><label class="checkbox-row"><input type="checkbox" name="published" ${active?.published?'checked':''}> Công khai câu luyện tập cho sinh viên</label><div data-question-editor>${selectedKind==='code'?window.examConfig.problemView(problem):`<label>Tên câu hỏi<input data-question-title required maxlength="200" value="${esc(problem.title||'')}"></label><label>Nội dung / yêu cầu<textarea data-question-statement rows="6" maxlength="20000">${esc(problem.statement||'')}</textarea></label>`}</div><div class="bridge-inline"><button class="btn btn-primary">Lưu câu hỏi</button><button type="button" class="btn btn-ghost" data-question-cancel>Đóng</button></div><p class="ref-form-error" data-question-error role="alert"></p></form></section>`:''}<section class="panel"><div class="panel-heading"><div><h2>Đề thi từ ngân hàng</h2><p class="muted">Chọn câu hỏi trong khóa, đặt số câu sẽ phát ngẫu nhiên cho mỗi sinh viên.</p></div></div><div class="student-admin-list">${papers.map(p=>`<div class="student-row"><div class="student-row-body"><strong>${esc(p.title)}</strong><p class="muted">${kind[p.kind]} · ${p.question_count}/${p.question_ids.length} câu mỗi sinh viên</p></div></div>`).join('')||'<p class="muted">Chưa có đề thi.</p>'}</div><form class="stack-form" data-paper-form><input type="hidden" name="course_id" value="${esc(c.id)}"><div class="two-cols"><label>Tên đề thi<input name="title" required maxlength="200"></label><label>Hình thức<select name="kind" data-paper-kind><option value="code">Thi lập trình</option><option value="file">Thi nộp file</option></select></label></div><div data-paper-choices>${choices(questions,'code')}</div><label>Số câu phát cho mỗi sinh viên<input type="number" name="question_count" min="1" max="30" value="1" required></label><div><button class="btn btn-primary">Lưu đề thi</button></div><p class="ref-form-error" data-paper-error role="alert"></p></form></section>`;
  }
  function choices(questions,type){return questions.filter(q=>q.kind===type&&q.category==='exam').map(q=>`<label class="checkbox-row"><input type="checkbox" name="question_ids" value="${q.id}"> ${esc(q.problem.title)} · ${category[q.category]}</label>`).join('')||'<p class="muted">Chưa có câu hỏi loại thi thuộc hình thức này.</p>';}
  function problem(form){
    const p=form.querySelector('[data-program-problem]');
    if(!p)return {title:form.querySelector('[data-question-title]').value,statement:form.querySelector('[data-question-statement]').value};
    return {title:p.querySelector('[data-problem-title]').value,statement:p.querySelector('[data-problem-statement]').value,points:p.querySelector('[data-problem-points]').value,time_limit_ms:p.querySelector('[data-problem-time]').value,memory_limit_mb:p.querySelector('[data-problem-memory]').value,checker:p.querySelector('[data-problem-checker]').value,execution_mode:p.querySelector('[data-problem-mode]').value,tests:[...p.querySelectorAll('[data-program-test]')].map(t=>({input:t.querySelector('[data-test-input]').value,output:t.querySelector('[data-test-output]').value,test_code:t.querySelector('[data-test-code]').value,sample:t.querySelector('[data-test-sample]').checked}))};
  }
  function handleClick(event,data,c,rerender){
    const target=event.target;
    if(target.closest('[data-question-new]')){editor='new';selectedKind='code';rerender();return true;}
    const edit=target.closest('[data-question-edit]');if(edit){editor=edit.dataset.questionEdit;selectedKind=byCourse(data,c).find(q=>q.id===editor)?.kind||'code';rerender();return true;}
    if(target.closest('[data-question-cancel]')){editor='';rerender();return true;}
    const row=target.closest('[data-question-form] [data-program-problem]');
    if(row&&target.closest('[data-test-add]')){row.querySelector('[data-test-list]').insertAdjacentHTML('beforeend',window.examConfig.testView());return true;}
    if(row&&target.closest('[data-test-remove]')){target.closest('[data-program-test]').remove();return true;}
    if(row&&target.closest('[data-test-import]')){window.examConfig.importTests(row);return true;}
    return false;
  }
  async function handleSubmit(event,load){
    const form=event.target;
    if(form.matches('[data-question-form]')){
      event.preventDefault();
      if(!form.reportValidity())return true;
      const body=new FormData(form);body.set('published',form.elements.published.checked?'true':'false');body.set('problem',JSON.stringify(problem(form)));
      try{await window.cssRequest('/api/admin/questions/save',{method:'POST',body});editor='';await load();window.cssToast('Đã lưu câu hỏi.','success');}catch(error){form.querySelector('[data-question-error]').textContent=error.message;}
      return true;
    }
    if(form.matches('[data-paper-form]')){
      event.preventDefault();
      if(!form.reportValidity())return true;
      const body=new FormData(form);body.set('question_ids',[...form.querySelectorAll('[name=question_ids]:checked')].map(n=>n.value).join(' '));
      try{await window.cssRequest('/api/admin/papers/save',{method:'POST',body});await load();window.cssToast('Đã lưu đề thi. Chọn đề khi cấu hình kỳ thi.','success');}catch(error){form.querySelector('[data-paper-error]').textContent=error.message;}
      return true;
    }
    return false;
  }
  window.questionBank={view,choices,handleClick,handleSubmit,reset(){editor='';},setKind(value){selectedKind=value;}};
})();
