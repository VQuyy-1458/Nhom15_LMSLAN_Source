(() => {
  'use strict';
  const esc = window.cssEscape;
  const selectedWeeks = new Map();
  const contexts = new Map();
  const localDay = value => new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Ho_Chi_Minh', year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date(value));
  const labelDay = value => new Intl.DateTimeFormat('vi-VN', {timeZone:'Asia/Ho_Chi_Minh', day:'2-digit', month:'2-digit'}).format(new Date(value));
  const labelDate = value => new Intl.DateTimeFormat('vi-VN', {timeZone:'Asia/Ho_Chi_Minh', dateStyle:'short', timeStyle:'short'}).format(new Date(value));
  function weekStart(value) {
    const day = new Date(localDay(value) + 'T12:00:00Z');
    day.setUTCDate(day.getUTCDate() - (day.getUTCDay() + 6) % 7);
    return day.toISOString().slice(0, 10);
  }
  function weekLabel(key) {
    const start = new Date(key + 'T12:00:00Z'), end = new Date(start);
    end.setUTCDate(end.getUTCDate() + 6);
    return `${labelDay(start)} – ${labelDay(end)}`;
  }
  function item(row, kind, admin, lessons=[], courseId='', editable=true) {
    const icon = kind === 'material' ? 'book' : kind === 'assignment' ? 'file-text-o' : 'bullhorn';
    const action = admin ? `data-tab="${kind === 'material' ? 'materials' : kind === 'assignment' ? 'assignments' : 'calendar'}"` : `data-learning-detail="${kind === 'notice' ? 'event' : kind}" data-item="${esc(row.id)}"`;
    const meta = kind === 'assignment' ? `Hạn ${labelDate(row.due_at)}` : kind === 'material' ? `Đăng ${labelDate(row.created_at)}` : labelDate(row.starts_at);
    const link = admin && editable && kind !== 'notice' ? `<form class="course-week-link-form" data-action="link-content"><input type="hidden" name="course_id" value="${esc(courseId)}"><input type="hidden" name="kind" value="${kind === 'material' ? 'materials' : 'assignments'}"><input type="hidden" name="item_id" value="${esc(row.id)}"><select name="lesson_id" aria-label="Buổi học cho ${esc(row.title)}"><option value="">Chưa gắn buổi</option>${lessons.map(lesson=>`<option value="${esc(lesson.id)}" ${lesson.id===row.lesson_id?'selected':''}>${esc(labelDate(lesson.starts_at))} · ${esc(lesson.title)}</option>`).join('')}</select><button type="submit" class="btn btn-secondary">Lưu buổi</button></form>` : '';
    return `<div class="course-week-item" data-activity="${kind === 'notice' ? 'announcement' : kind}"><i class="fa fa-${icon}" aria-hidden="true"></i><div><button type="button" class="course-week-link" ${action}>${esc(row.title)}</button><small>${esc(meta)}</small>${link}</div></div>`;
  }
  function render(data, course, {admin=false}={}) {
    const contextKey = `${admin ? 'admin' : 'student'}:${course.id}`;
    contexts.set(contextKey, {data,course,admin});
    const lessons = data.events.filter(row => row.course_id === course.id && row.kind === 'lesson').sort((a,b) => a.starts_at.localeCompare(b.starts_at));
    const materials = data.materials.filter(row => row.course_id === course.id);
    const assignments = data.assignments.filter(row => row.course_id === course.id);
    const notices = data.events.filter(row => row.course_id === course.id && row.kind === 'announcement');
    const weeks = new Map();
    for (const lesson of lessons) {
      const key = weekStart(lesson.starts_at);
      if (!weeks.has(key)) weeks.set(key, []);
      weeks.get(key).push(lesson);
    }
    for (const notice of notices) if (!weeks.has(weekStart(notice.starts_at))) weeks.set(weekStart(notice.starts_at), []);
    const known = new Set(lessons.map(row => row.id));
    const looseMaterials = materials.filter(row => !known.has(row.lesson_id));
    const looseAssignments = assignments.filter(row => !known.has(row.lesson_id));
    const keys = [...weeks.keys()].sort();
    const hasUnassigned = Boolean(looseMaterials.length || looseAssignments.length);
    let selected = selectedWeeks.get(contextKey);
    if (!keys.includes(selected) && !(selected === 'unassigned' && hasUnassigned)) selected = '';
    selectedWeeks.set(contextKey, selected);
    const index = keys.indexOf(selected);
    const sections = keys.filter(key=>key===selected).map(key => {
      const classes = weeks.get(key);
      const content = classes.map(lesson => {
        const attachedMaterials = materials.filter(row => row.lesson_id === lesson.id);
        const attachedAssignments = assignments.filter(row => row.lesson_id === lesson.id);
        const lessonAction = admin ? `data-lesson-open="${esc(lesson.id)}"` : `data-learning-detail="event" data-item="${esc(lesson.id)}"`;
        return `<div class="course-week-lesson"><div class="course-week-lesson-head"><span class="course-week-date">${esc(labelDate(lesson.starts_at))}</span><button type="button" class="course-week-link" ${lessonAction}>${esc(lesson.title)}</button>${lesson.location ? `<span class="muted">${esc(lesson.location)}</span>` : ''}</div>${lesson.description ? `<p class="course-week-description">${esc(lesson.description)}</p>` : ''}<div class="course-week-resources">${attachedMaterials.map(row=>item(row,'material',admin,lessons,course.id,course.status!=='completed')).join('')}${attachedAssignments.map(row=>item(row,'assignment',admin,lessons,course.id,course.status!=='completed')).join('') || (!attachedMaterials.length ? '<small class="muted">Chưa có tài liệu hoặc bài tập cho buổi này.</small>' : '')}</div></div>`;
      }).join('');
      const announcements = notices.filter(row => weekStart(row.starts_at) === key);
      return `<section class="course-week"><header><span><strong>Tuần ${index+1}</strong><small>${weekLabel(key)}</small></span><span>${classes.length} buổi · ${materials.filter(row=>classes.some(lesson=>lesson.id===row.lesson_id)).length} tài liệu · ${assignments.filter(row=>classes.some(lesson=>lesson.id===row.lesson_id)).length} bài tập</span></header><div class="course-week-body">${content || '<p class="muted">Chưa có buổi học trong tuần này.</p>'}${announcements.length ? `<div class="course-week-notices"><strong>Thông báo trong tuần</strong>${announcements.map(row=>item(row,'notice',admin)).join('')}</div>` : ''}</div></section>`;
    }).join('');
    const unassigned = looseMaterials.length || looseAssignments.length ? `<section class="course-week-unassigned"><h3>Nội dung chưa gắn buổi học</h3><p class="muted">${admin && course.status!=='completed' ? 'Chọn buổi học và lưu để xếp nội dung cũ vào tiến độ.' : 'Các nội dung này chưa được xếp vào buổi học cụ thể.'}</p><div class="course-week-resources">${looseMaterials.map(row=>item(row,'material',admin,lessons,course.id,course.status!=='completed')).join('')}${looseAssignments.map(row=>item(row,'assignment',admin,lessons,course.id,course.status!=='completed')).join('')}</div></section>` : '';
    const options = keys.map((key,i)=>`<option value="${key}" ${key===selected?'selected':''}>Tuần ${i+1} · ${weekLabel(key)}</option>`).join('');
    const controls = `<div class="course-week-picker"><label for="course-week-${esc(contextKey)}">Chọn tuần</label><button type="button" data-course-week-step="-1" ${index<=0?'disabled':''} aria-label="Tuần trước"><i class="fa fa-chevron-left"></i></button><select id="course-week-${esc(contextKey)}" data-course-week-select aria-label="Chọn tuần học"><option value="" ${selected===''?'selected':''}>-- Chọn tuần để xem nội dung --</option>${options}${hasUnassigned?`<option value="unassigned" ${selected==='unassigned'?'selected':''}>Nội dung chưa gắn buổi</option>`:''}</select><button type="button" data-course-week-step="1" ${index<0||index>=keys.length-1?'disabled':''} aria-label="Tuần sau"><i class="fa fa-chevron-right"></i></button></div>`;
    return `<section class="panel course-week-board" data-course-week-context="${esc(contextKey)}"><div class="student-section-head"><div><h2>Học theo tuần</h2><p class="muted">Chọn tuần để xem bài học, tài liệu và bài tập.</p></div><span class="muted">${keys.length} tuần · ${lessons.length} buổi</span></div>${keys.length||hasUnassigned?controls:''}${sections || (selected==='unassigned'?unassigned:keys.length||hasUnassigned?'<p class="muted">Hãy chọn một tuần ở trên để xem nội dung.</p>':'<p class="muted">Chưa có buổi học nào trong khóa học.</p>')}</section>`;
  }
  function update(board, value) {
    const contextKey=board.dataset.courseWeekContext, context=contexts.get(contextKey);
    if (!context) return;
    selectedWeeks.set(contextKey,value);
    board.outerHTML=render(context.data,context.course,{admin:context.admin});
  }
  document.addEventListener('change',event=>{
    if (event.target.matches('[data-course-week-select]')) update(event.target.closest('[data-course-week-context]'),event.target.value);
  });
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-course-week-step]');if(!button)return;
    const board=button.closest('[data-course-week-context]'),select=board.querySelector('[data-course-week-select]');
    const keys=[...select.options].map(option=>option.value).filter(value=>value!=='unassigned');
    const target=keys[keys.indexOf(select.value)+Number(button.dataset.courseWeekStep)];
    if(target)update(board,target);
  });
  function weekOptions(data,courseId,selected='') {
    const lessons=data.events.filter(row=>row.course_id===courseId&&row.kind==='lesson');
    const keys=[...new Set(lessons.map(row=>weekStart(row.starts_at)))].sort();
    return `<option value="">Tất cả tuần</option>${keys.map((key,i)=>`<option value="${key}" ${selected===key?'selected':''}>Tuần ${i+1} · ${weekLabel(key)}</option>`).join('')}<option value="unassigned" ${selected==='unassigned'?'selected':''}>Chưa gắn buổi</option>`;
  }
  function matchesWeek(row,data,week) {
    if (!week) return true;
    const lesson=data.events.find(event=>event.id===row.lesson_id&&event.course_id===row.course_id&&event.kind==='lesson');
    return week==='unassigned' ? !lesson : Boolean(lesson&&weekStart(lesson.starts_at)===week);
  }
  window.courseWeeks = {render,weekOptions,matchesWeek};
})();
