/* Show the selected lesson's attendance, with editable records after closing. */
(() => {
  'use strict';
  const esc=window.cssEscape;
  const date=v=>new Intl.DateTimeFormat('vi-VN',{timeZone:'Asia/Ho_Chi_Minh',dateStyle:'short',timeStyle:'short'}).format(new Date(v));
  const labels={present:'Có mặt',late:'Đến muộn',early_departure:'Về sớm',absent:'Vắng',unrecorded:'Chưa điểm danh',excluded:'Không tính điểm'};
  const attended=new Set(['present','late','early_departure']);
  const status=(label,open)=>`<span class="bridge-pill ${open?'green':''}">${label}</span>`;
  function view(data,course,id='',page=1,query=''){
    const sessions=window.listUi.view('course:attendance:'+course.id,data.attendance.filter(s=>s.course_id===course.id),'attendance');
    const members=data.students.filter(s=>course.student_ids===null||course.student_ids.includes(s.student_id)),readonly=course.status==='completed';
    if(!id)return `<section class="panel"><div class="ref-heading-row"><div><h2>Điểm danh theo buổi học</h2><p class="muted">Chọn một buổi để xem danh sách sinh viên và quản lý điểm danh.</p></div><button type="button" class="btn btn-secondary" data-tab="calendar">Chọn buổi học trên lịch</button></div>${window.listUi.controls('course:attendance:'+course.id,'attendance')}<div class="attendance-session-list">${sessions.map(s=>{const eligible=members.filter(m=>!s.excluded_student_ids?.includes(m.student_id)),present=eligible.filter(m=>attended.has(s.records[m.student_id]?.status)).length;return `<button type="button" class="attendance-session-row activity-surface" data-activity="attendance" data-attendance-open="${s.id}"><span class="ref-resource-symbol"><i class="fa fa-check-square-o"></i></span><span class="attendance-session-label"><strong>${esc(s.title)}</strong><small>Hạn ${date(s.expires_at)} · ${present}/${eligible.length} đã điểm danh</small></span>${status(s.open?'Đang mở':'Đã kết thúc',s.open)}<i class="fa fa-angle-right"></i></button>`;}).join('')||'<div class="ref-empty">Chưa có phiên điểm danh trong khóa học này.</div>'}</div></section>`;
    const s=data.attendance.find(row=>row.id===id&&row.course_id===course.id),back='<div class="attendance-back-row"><button type="button" class="btn btn-ghost attendance-back" data-attendance-back><i class="fa fa-arrow-left"></i> Quay lại danh sách buổi điểm danh</button></div>';
    if(!s)return back+'<section class="panel"><div class="ref-empty">Không tìm thấy buổi điểm danh trong khóa học đang chọn.</div></section>';
    const eligible=members.filter(m=>!s.excluded_student_ids?.includes(m.student_id));
    const present=eligible.filter(m=>attended.has(s.records[m.student_id]?.status)).length;
    const late=eligible.filter(m=>s.records[m.student_id]?.status==='late').length;
    const early=eligible.filter(m=>s.records[m.student_id]?.status==='early_departure').length;
    const filtered=window.listUi.view('course:attendance-members:'+id,members.filter(m=>(m.student_id+' '+m.full_name).toLocaleLowerCase('vi').includes(query.toLocaleLowerCase('vi'))).map(m=>{
      const record=s.records[m.student_id],attendance_status=s.excluded_student_ids?.includes(m.student_id)?'excluded':record?.status||(s.open?'unrecorded':'absent');
      return {...m,attendance_status,checked_in_at:record?.checked_in_at};
    }),'attendancePeople',{search:false}),pages=Math.max(1,Math.ceil(filtered.length/10));
    page=Math.max(1,Math.min(page,pages));
    const note=s.attendance_method==='lan-online'?'<p class="muted">Sinh viên đang đăng nhập khi mở phiên được tự ghi nhận có mặt. Sinh viên đăng nhập sau đó sẽ tự được cập nhật vào danh sách khi hệ thống nhận hoạt động.</p>':'';
    return `${back}<section class="panel attendance-session-detail" data-attendance-detail="${s.id}"><div class="ref-heading-row"><div><h2>${esc(s.title)}</h2><p class="muted">Hạn ${date(s.expires_at)} · ${esc(course.name)}</p></div>${status(s.open?'Đang mở':'Đã kết thúc',s.open)}</div>${s.description?`<p class="student-description">${esc(s.description)}</p>`:''}${note}${window.courseDesign.stats([['Sĩ số tính điểm',eligible.length,'users'],['Đã điểm danh',present,'check'],['Đến muộn',late,'clock-o'],['Về sớm',early,'sign-out']])}<form class="ref-toolbar" id="attendance-search-form"><label class="ref-search"><i class="fa fa-search"></i><input name="query" aria-label="Tìm sinh viên trong buổi điểm danh" placeholder="Tìm MSSV hoặc họ tên…" value="${esc(query)}"></label><button class="btn btn-secondary">Tìm kiếm</button></form>${window.listUi.controls('course:attendance-members:'+id,'attendancePeople')}<div class="table-wrap"><table class="attendance-detail-table"><thead><tr><th>MSSV</th><th>Họ tên</th><th>Trạng thái</th><th>Thời gian</th><th>Ghi chú</th></tr></thead><tbody>${filtered.slice((page-1)*10,page*10).map(m=>{const r=s.records[m.student_id],state=m.attendance_status;return `<tr><td>${esc(m.student_id)}</td><td><strong>${esc(m.full_name)}</strong></td><td><span class="bridge-pill ${state==='present'?'green':state==='late'?'amber':state==='early_departure'?'blue':state==='absent'?'red':''}">${labels[state]||'Chưa điểm danh'}</span></td><td>${r?.checked_in_at?date(r.checked_in_at):'—'}</td><td>${esc(state==='excluded'?'Buổi học trước khi tham gia; không trừ chuyên cần':r?.reason||'—')}</td></tr>`;}).join('')||'<tr><td colspan="5">Không tìm thấy sinh viên phù hợp.</td></tr>'}</tbody></table></div><div class="attendance-pagination"><span>${filtered.length} sinh viên</span><div><button type="button" class="btn btn-secondary" data-attendance-page="${page-1}" ${page===1?'disabled':''}>Trước</button><span>Trang ${page}/${pages}</span><button type="button" class="btn btn-secondary" data-attendance-page="${page+1}" ${page===pages?'disabled':''}>Sau</button></div></div>${!readonly&&s.open?`<form class="ref-actions" data-action="close-attendance"><input name="session_id" type="hidden" value="${s.id}"><button class="btn btn-secondary">Kết thúc điểm danh</button></form><p class="muted">Sau khi kết thúc, thầy vẫn có thể chỉnh trạng thái trong danh sách.</p>`:readonly?'<p class="muted">Khóa học đã tổng kết. Danh sách chỉ xem.</p>':'<p class="muted">Danh sách đã kết thúc. Thầy vẫn có thể chỉnh trạng thái.</p>'}</section>`;
  }
  function decorate(root,data,course,id){
    const session=data.attendance.find(row=>row.id===id&&row.course_id===course.id);
    if(!session||course.status==='completed')return;
    const excluded=new Set(session.excluded_student_ids||[]);
    root.querySelectorAll('.attendance-detail-table tbody tr').forEach(row=>{
      const studentId=row.cells[0]?.textContent.trim(),cell=row.cells[2];
      if(!studentId||!cell||excluded.has(studentId)||cell.querySelector('.attendance-choices'))return;
      const current=session.records[studentId]?.status;
      const choices=[['present','Có mặt'],['late','Đến muộn'],['early_departure','Về sớm'],['absent','Vắng']];
      cell.insertAdjacentHTML('beforeend',`<div class="attendance-choices" role="group" aria-label="Điểm danh ${esc(studentId)}">${choices.map(([value,label])=>`<button type="button" class="attendance-choice ${current===value?'is-selected':''}" data-attendance-choice="${value}" data-student-id="${esc(studentId)}" aria-pressed="${current===value}"><i class="fa fa-check" aria-hidden="true"></i> ${label}</button>`).join('')}</div>`);
    });
  }
  window.classroomAttendance={view,decorate};
})();
