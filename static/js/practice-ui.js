/* Public-to-enrolled-students practice questions; no course-grade contribution. */
(() => {
  'use strict';
  const esc=window.cssEscape;
  function render(data,scope=''){
    const code=(data.programming?.exams||[]).filter(e=>e.practice&&(!scope||e.course_id===scope));
    const files=data.assignments.filter(e=>e.practice&&(!scope||e.course_id===scope));
    return `<section class="panel"><h2>Tự luyện tập</h2><p>Chọn bài đã được công bố trong các lớp bạn tham gia. Không cần giảng viên giao riêng; kết quả luyện tập không tính vào điểm khóa học.</p><div class="two-cols"><label>Tìm bài luyện tập<input type="search" data-practice-search placeholder="Tên bài"></label><label>Hình thức<select data-practice-format><option value="">Tất cả</option><option value="code">Code</option><option value="file">Nộp file</option></select></label></div><div class="resource-lines">${[...code.map(q=>({...q,format:'code'})),...files.map(q=>({...q,format:'file'}))].map(q=>`<details class="resource-line" data-practice-row data-format="${q.format}" data-title="${esc(q.title.toLocaleLowerCase('vi'))}"><summary><span class="resource-line-title">${esc(q.title)}</span><span>${q.format==='code'?'Code':'Nộp file'} · ${esc(data.courses.find(c=>c.id===q.course_id)?.name||'')}</span></summary><div class="resource-line-body">${window.classificationUI.badges(q)}<p>${esc(q.description||'Bài luyện tập tự chọn.')}</p>${q.format==='code'?`<a class="btn btn-primary" href="/student/assignments?mode=practice&exam=${encodeURIComponent(q.id)}&course=${encodeURIComponent(q.course_id)}">Mở bài / Viết code</a>`:`<button type="button" class="btn btn-primary" data-learning-detail="assignment" data-item="${esc(q.id)}">Xem yêu cầu & nộp file</button>`}</div></details>`).join('')||'<p>Chưa có bài luyện tập được công bố trong lớp của bạn.</p>'}</div></section>`;
  }
  document.addEventListener('input',filter);
  document.addEventListener('change',filter);
  function filter(event){if(!event.target.matches('[data-practice-search],[data-practice-format]'))return;
    const root=event.target.closest('.panel'),query=root.querySelector('[data-practice-search]').value.toLocaleLowerCase('vi'),format=root.querySelector('[data-practice-format]').value;
    root.querySelectorAll('[data-practice-row]').forEach(row=>row.hidden=!row.dataset.title.includes(query)||(!!format&&format!==row.dataset.format));
  }
  function tabs(scope){return `<div class="bridge-inline"><a class="btn btn-secondary" href="/student/assignments${scope?'?course='+encodeURIComponent(scope):''}">Bài được giao</a><a class="btn btn-secondary" href="/student/assignments?mode=practice${scope?'&course='+encodeURIComponent(scope):''}">Tự luyện tập</a></div>`;}
  window.practiceUI={render,tabs,label:'Tự luyện · Không tính điểm khóa học'};
})();
