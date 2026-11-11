/* Homework management reuses the exam problem/test editor and grading views. */
(() => {
  'use strict';
  const esc=window.cssEscape;
  let context=null,refresh=async()=>{};
  const local=value=>value?new Date(Date.parse(value)+7*3600000).toISOString().slice(0,16):'';
  const date=value=>new Date(value).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'});
  function listSections(drafts,render){
    return `<section class="panel" data-pa-drafts><h2>Bản nháp bài tập lập trình (${drafts.length})</h2><p class="muted">Chọn Giao bài để chuyển vào danh sách bài tập chính thức phía trên.</p><div class="resource-lines">${drafts.map(render).join('')||'<p class="muted">Không có bản nháp.</p>'}</div></section>`;
  }
  function publishedRow(row){
    return `<details class="resource-line activity-surface" data-activity="assignment" data-pa-published="${esc(row.id)}"><summary><i class="fa fa-code" aria-hidden="true"></i><span class="resource-line-title">${esc(row.title)}</span><span class="bridge-pill">Lập trình</span><span class="resource-line-meta">Hạn ${esc(date(row.due_at))}</span><span class="bridge-pill" data-deadline-status data-expires-at="${esc(row.due_at)}">${Date.parse(row.due_at)<=Date.now()?'Đã đóng':'Đang nhận bài'}</span></summary><div class="resource-line-body">${row.topic?`<p class="muted">${esc(row.topic)}</p>`:''}${window.classificationUI?.badges(row)||''}<p class="student-description">${esc(row.description||'Chưa có mô tả.')}</p><p>${row.programming.problems.length} bài toán · ${row.participants.length} học viên · ${row.programming.languages.map(esc).join(', ')}</p><div class="ref-actions"><button type="button" class="btn btn-secondary" data-pa-results="${esc(row.id)}">Kết quả & lịch sử chấm</button></div></div></details>`;
  }
  function adminList(data,course){
    context={data,course};
    const items=(data.programming_assignments||[]).filter(r=>r.course_id===course.id),closed=course.status==='completed';
    const render=r=>`<details class="resource-line"><summary><span class="resource-line-title">${esc(r.title)}</span><span class="resource-line-meta">${r.state==='idle'?'Bản nháp':'Đã giao · Chính thức'} · Hạn ${esc(date(r.due_at))}</span></summary><div class="resource-line-body"><p class="student-description">${esc(r.description)}</p><p>${r.programming.problems.length} bài toán · ${r.participants.length} học viên · ${r.programming.languages.map(esc).join(', ')}</p><div class="ref-actions">${r.state==='idle'&&!closed?`<button type="button" class="btn btn-secondary" data-pa-edit="${r.id}">Sửa đề & test</button><button type="button" class="btn btn-primary" data-pa-assign="${r.id}">Giao bài</button><button type="button" class="btn btn-danger" data-pa-delete="${r.id}">Xóa bản nháp</button>`:''}<button type="button" class="btn btn-secondary" data-pa-results="${r.id}">Kết quả & lịch sử chấm</button></div></div></details>`;
    const drafts=items.filter(r=>r.state==='idle');
    return (window.questionLibraryUI?.practicalButton(course.id)||'')+listSections(drafts,render);
  }

  function editor(row={}){
    const dialog=window.adminDesign.modal(row.id?'Sửa bài tập lập trình':'Tạo bài tập lập trình',`<form class="stack-form" data-pa-save><input type="hidden" name="type" value="programming"><input type="hidden" name="id" value="${esc(row.id||'')}"><input type="hidden" name="course_id" value="${esc(context.course.id)}"><label>Tên bài tập<input name="title" required maxlength="200" value="${esc(row.title||'')}"></label><label>Chủ đề / tuần<input name="topic" maxlength="200" value="${esc(row.topic||'')}" placeholder="Tuần 1 · Vòng lặp"></label><label>Mô tả<textarea name="description" rows="3" maxlength="10000">${esc(row.description||'')}</textarea></label><label>Hạn nộp (giờ Việt Nam)<input name="due_at" type="datetime-local" value="${local(row.due_at)}" required></label>${window.classificationUI?.fields(row)||''}${window.examConfig.programmingFields(row)}<section data-exam-bank></section><p class="muted">Bài tập dùng hạn nộp ở trên. Lưu bản nháp rồi bấm Giao bài để học viên bắt đầu làm.</p><button class="btn btn-primary">Lưu bản nháp</button><p class="ref-form-error" role="alert" data-pa-error></p></form>`);
    void window.examConfig.loadBank(dialog.querySelector('form'),row);
    const heading=dialog.querySelector('.exam-programming .bridge-section-toolbar h3');
    if(heading)heading.textContent='Bài toán trong bài tập';
    const note=dialog.querySelector('.exam-programming > .fine-print');
    if(note)note.textContent='Chọn test mẫu để học viên chạy thử. Khi nộp bài, hệ thống chấm cả test mẫu và test ẩn. Lưu bản nháp rồi giao bài cho học viên trước hạn nộp.';
    window.examConfig.showProblem(dialog.querySelector('[data-program-problem]'));
  }
  document.addEventListener('click',async event=>{
    if(!context)return;
    const button=event.target.closest('[data-pa-create],[data-pa-edit],[data-pa-assign],[data-pa-delete],[data-pa-results]');
    if(!button)return;
    const rows=context.data.programming_assignments||[];
    if(button.hasAttribute('data-pa-create')){editor();return;}
    const id=button.dataset.paEdit||button.dataset.paAssign||button.dataset.paDelete||button.dataset.paResults;
    const row=rows.find(r=>r.id===id);if(!row)return;
    if(button.hasAttribute('data-pa-edit')){editor(row);return;}
    if(button.hasAttribute('data-pa-assign')){
      const students=context.data.students.filter(s=>s.active!==false&&(context.course.student_ids===null||context.course.student_ids.includes(s.student_id)));
      window.adminDesign.modal('Giao bài: '+row.title,`<form class="stack-form" data-pa-give><input type="hidden" name="id" value="${row.id}"><p>Chọn học viên được giao bài. Đề và test sẽ được khóa sau khi giao.</p>${students.map(s=>`<label class="checkbox-row"><input type="checkbox" name="student" value="${esc(s.student_id)}" checked> ${esc(s.student_id)} · ${esc(s.full_name)}</label>`).join('')||'<p>Chưa có học viên trong lớp.</p>'}<button class="btn btn-primary">Giao bài</button><p class="ref-form-error" role="alert" data-pa-error></p></form>`);return;
    }
    try{
      if(button.hasAttribute('data-pa-delete')){
        if(!confirm('Xóa bản nháp bài tập này?'))return;
        await window.cssRequest('/api/admin/programming-assignments/delete',{method:'POST',body:new URLSearchParams({id})});await refresh();return;
      }
      const dialog=window.adminDesign.modal('Kết quả: '+row.title,`<div data-code-admin-results="${row.id}">Đang tải kết quả…</div>`);
      const result=await window.cssRequest('/api/admin/programming/submissions?exam='+encodeURIComponent(id));
      if(dialog.isConnected)dialog.querySelector('[data-code-admin-results]').innerHTML=result.submissions.map(r=>window.programmingUi.result(r,true)).join('')||'<p>Chưa có bài nộp.</p>';
    }catch(error){window.cssToast(error.message,'error');}
  });
  // Capture these forms before the course editor's generic submit listener.
  document.addEventListener('submit',async event=>{
    const form=event.target;if(!form.matches('[data-pa-save],[data-pa-give]'))return;
    event.preventDefault();event.stopImmediatePropagation();if(form.dataset.saving)return;
    if(!form.reportValidity())return;
    form.dataset.saving='true';const button=form.querySelector('button:not([type])');button.disabled=true;
    try{
      const save=form.hasAttribute('data-pa-save'),body=save?window.examConfig.payload(form):new FormData(form);
      if(save)body.set('due_at',new Date(body.get('due_at')+'+07:00').toISOString());
      else body.set('student_ids',[...form.querySelectorAll('[name=student]:checked')].map(n=>n.value).join(','));
      const result=await window.cssRequest('/api/admin/programming-assignments/'+(save?'save':'assign'),{method:'POST',body});
      window.adminDrafts?.saved(form);form.closest('dialog')?.close();
      await refresh();
      window.cssToast(save?'Đã lưu bản nháp bài tập.':`Đã giao bài chính thức cho ${result.participant_count??body.get('student_ids').split(',').filter(Boolean).length} học viên.`,'success');
    }catch(error){form.querySelector('[data-pa-error]').textContent=error.message;}
    finally{delete form.dataset.saving;button.disabled=false;}
  },true);
  window.programmingAssignmentsUI={adminList,publishedRow,configure(options){refresh=options.refresh;}};
})();
