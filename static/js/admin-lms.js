/* Course context above the existing, detailed submission administration. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id),esc=window.cssEscape;
  const section=document.querySelector('.admin-shell').dataset.adminSection;
  const params=new URLSearchParams(location.search),scope=params.get('course')||'';
  let data,review=params.get('assignment')||'';
  const date=v=>v?new Intl.DateTimeFormat('vi-VN',{timeZone:'Asia/Ho_Chi_Minh',dateStyle:'short',timeStyle:'short'}).format(new Date(v)):'Chưa đặt lịch';
  const courseUrl=(id,tab='')=>`/admin/courses?course=${encodeURIComponent(id)}${tab?'&tab='+tab:''}`;
  const pageUrl=(name,id=scope,extra='')=>`/admin?section=${name}${id?'&course='+encodeURIComponent(id):''}${extra}`;
  const name=id=>data.courses.find(c=>c.id===id)?.name||'Kỳ thi chung';
  const pill=(label,color='')=>`<span class="bridge-pill ${color}">${esc(label)}</span>`;
  const empty=(title,message)=>`<div class="bridge-empty"><i class="fa fa-folder-open-o"></i><h3>${esc(title)}</h3><p>${esc(message)}</p></div>`;
  const stat=(icon,color,label,value)=>`<article class="stat-card"><span class="stat-icon ${color}"><i class="fa fa-${icon}"></i></span><div><p>${label}</p><strong>${value}</strong></div></article>`;
  const enrolled=id=>data.students.filter(s=>{const c=data.courses.find(c=>c.id===id);return c&&(c.student_ids===null||c.student_ids.includes(s.student_id));});
  function context(){
    const node=$('admin-course-context');if(!node)return;
    node.innerHTML=`<form id="admin-scope-form"><label for="admin-course-picker"><i class="fa fa-book"></i> Khóa học</label><select id="admin-course-picker" name="course"><option value="">Tất cả khóa học</option>${data.courses.map(c=>`<option value="${c.id}" ${scope===c.id?'selected':''}>${esc(c.name)} · ${esc(c.code)}</option>`).join('')}</select></form><a class="bridge-text-link" href="${scope?courseUrl(scope):'/admin/courses'}">${scope?'Mở không gian khóa học':'Xem danh sách khóa học'} <i class="fa fa-arrow-right"></i></a>`;
    if(section==='monitor'){
      const exams=data.exams.filter(e=>!scope||e.course_id===scope),selected=params.get('exam')||'';
      const label=document.createElement('label');label.className='monitor-exam-picker';label.innerHTML=`Kỳ thi<select id="admin-monitor-exam"><option value="">Tổng quan sinh viên</option>${exams.map(e=>`<option value="${esc(e.id)}" ${e.id===selected?'selected':''}>${esc(e.title)} · ${e.type==='programming'?'Code':'File'}</option>`).join('')}</select>`;
      const courseLabel=node.querySelector('label[for=admin-course-picker]');
      courseLabel.append($('admin-course-picker'));
      node.querySelector('form').append(label);
      $('admin-monitor-exam').addEventListener('change',event=>{const e=exams.find(e=>e.id===event.target.value);location.assign(pageUrl('monitor',e?.course_id||scope,e?'&exam='+encodeURIComponent(e.id):''));});
    }
    $('admin-course-picker').addEventListener('change',e=>location.assign(pageUrl(section,e.target.value)));
    $('admin-scope-form').addEventListener('submit',e=>{e.preventDefault();location.assign(pageUrl(section,$('admin-course-picker').value));});
    document.querySelectorAll('.sidebar-nav a').forEach(a=>{const url=new URL(a.href);if(url.pathname==='/admin'&&['monitor','exam','submissions'].includes(url.searchParams.get('section'))&&scope){url.searchParams.set('course',scope);a.href=url.pathname+url.search;}if(url.pathname==='/admin/courses'&&scope)a.href=courseUrl(scope);});
  }
  function courseCard(c){
    const lessons=c.lessons||[],past=lessons.filter(e=>Date.parse(e.starts_at)<=Date.now()).length,next=lessons.filter(e=>Date.parse(e.starts_at)>Date.now()).sort((a,b)=>Date.parse(a.starts_at)-Date.parse(b.starts_at))[0];
    return `<article class="bridge-course-card ui-course-card"><div class="bridge-course-cover"><span><i class="fa fa-book"></i></span>${pill('Đang giảng dạy','green')}</div><div class="bridge-course-body"><small class="bridge-course-code">${esc(c.code)}</small><h3>${esc(c.name)}</h3><p class="muted">${esc(c.semester)}</p><div class="bridge-course-progress"><span><i class="fa fa-users"></i> ${c.student_count} sinh viên</span><span>${lessons.length?`${past}/${lessons.length} buổi đã đến lịch`:'Chưa có lịch học'}</span></div>${lessons.length?`<progress value="${past}" max="${lessons.length}" aria-label="Số buổi đã đến lịch"></progress>`:''}<div class="bridge-course-next"><i class="fa fa-calendar-o"></i><span>${next?`${date(next.starts_at)}${next.location?' · '+esc(next.location):''}`:'Chưa có buổi học sắp tới'}</span></div><div class="bridge-course-footer"><a class="btn btn-secondary" href="${courseUrl(c.id)}">Mở khóa học</a>${pill(`${c.pending_count} bài chờ chấm`,c.pending_count?'amber':'')}</div></div></article>`;
  }
  window.listUi.on('dashboard',()=>dashboard());
  const monitorUrlSafe=e=>'/admin?section=monitor&course='+encodeURIComponent(e.course_id||'')+'&exam='+encodeURIComponent(e.id);
  function dashboard(){
    const active=window.listUi.view('dashboard:courses',data.courses.filter(c=>c.status==='active'),'courses',{statusFilter:false});
    const pending=data.courses.filter(c=>c.pending_count>0).sort((a,b)=>b.pending_count-a.pending_count);
    const live=data.exams.filter(e=>e.state==='started');
    $('admin-dashboard-overview').innerHTML=`<section class="panel"><div class="panel-heading ui-page-bar"><h2>Việc cần xử lý</h2><a class="btn btn-secondary" href="/admin?section=submissions">Tất cả bài nộp</a></div><ul class="ui-task-list">${pending.slice(0,5).map(c=>`<li><div><h3>${esc(c.name)}</h3><p class="muted">${c.pending_count} bài chờ chấm</p></div><a class="btn btn-secondary" href="/admin?section=submissions&course=${c.id}">Chấm bài</a></li>`).join('')}${live.map(e=>`<li><div><h3>${esc(e.title)}</h3><p class="muted">Kỳ thi đang mở</p></div><a class="btn btn-secondary" href="${monitorUrlSafe(e)}">Giám sát</a></li>`).join('')}${!pending.length&&!live.length?'<li>Không có công việc chờ xử lý.</li>':''}</ul></section><div class="teacher-dashboard-calendar" id="teacher-dashboard-calendar"></div><section class="panel bridge-teaching"><div class="panel-heading ui-page-bar"><h2>Khóa học đang giảng dạy</h2><a class="btn btn-secondary" href="/admin/courses">Tất cả khóa học</a></div><div class="bridge-course-grid ui-course-grid">${active.slice(0,6).map(courseCard).join('')}</div>${!active.length?empty('Chưa có khóa học đang giảng dạy','')+'<a class="btn btn-primary" href="/admin/courses">Tạo khóa học</a>':''}</section><nav class="bridge-dashboard-actions" aria-label="Thao tác nhanh"><a class="btn btn-secondary" href="/admin?section=monitor">Giám sát</a><a class="btn btn-secondary" href="/admin/question-bank">Kho bài tập & Đề</a><a class="btn btn-secondary" href="/admin?section=exam">Cấu hình kỳ thi</a></nav>`;
    window.teacherCalendar.mount($('teacher-dashboard-calendar'),data);
  }
  function examOverview(){window.examConfig.render(data);}
  function submissions(){window.submissionArchive.mount(data);}
  async function load(){try{data=await window.cssRequest('/api/admin/workspace'+(scope?'?course='+encodeURIComponent(scope):''));window.submissionDeadlines.sync(data.server_time);context();if($('admin-course-count'))$('admin-course-count').textContent=data.courses.length;if($('live-status'))$('live-status').textContent='Đã kết nối';if(section==='dashboard')dashboard();if(section==='exam')examOverview();if(section==='submissions')submissions();$('admin-workspace-error').classList.add('hidden');}catch(error){$('admin-workspace-error').textContent=error.message;$('admin-workspace-error').classList.remove('hidden');}}
  load();
  let deadlinePolling=false;
  async function pollDeadlines(){
    if(deadlinePolling||document.hidden||!data||!['exam','dashboard'].includes(section))return;
    deadlinePolling=true;
    try{
      const next=await window.cssRequest('/api/admin/workspace'+(scope?'?course='+encodeURIComponent(scope):''));
      window.submissionDeadlines.sync(next.server_time);
      if(section==='exam'){
        const id=params.get('exam'),times=d=>d.exams.filter(e=>!id||e.id===id).map(e=>[e.id,e.state,e.waiting,e.started_at,e.ends_at]),before=times(data),after=times(next);
        if(JSON.stringify(before)!==JSON.stringify(after)){
          // Keep an unfinished timing/configuration draft while refreshing its clock.
          if(window.adminDrafts?.dirty()){
            document.querySelectorAll('[data-exam-card], [data-exam-clock]').forEach(node=>{
              const e=next.exams.find(e=>e.id===(node.dataset.examCard||node.dataset.examClock));
              const clock=node.querySelector('.exam-wait-clock');
              if(clock&&e){if(e.waiting){clock.dataset.examOpensAt=e.started_at||e.scheduled_at;delete clock.dataset.openingHandled;clock.querySelector('[data-deadline-countdown]').dataset.expiresAt=e.started_at||e.scheduled_at;}else clock.remove();}
              if(e?.state==='started'&&!e.waiting&&node.matches('.exam-setup')){
                const fields=node.querySelector('#exam-config-form fieldset');if(fields)fields.disabled=true;
                document.querySelectorAll('[data-code-participant],#code-participants-form textarea,#code-participants-form button:not([data-list-clear])').forEach(n=>n.disabled=true);
                const status=node.querySelector('[data-auto-start-status]');if(status)status.textContent='Kỳ thi đã tự mở theo lịch. Cấu hình đã lưu được dùng cho kỳ thi; nội dung chưa lưu vẫn được giữ trong bản nháp.';
                const heading=node.querySelector('.panel-heading>.bridge-inline');if(heading&&!heading.querySelector('[data-exam-monitor]'))heading.insertAdjacentHTML('beforeend',window.examConfig.monitorLink(e));
                if(!document.querySelector('[data-exam-timing-form]'))node.insertAdjacentHTML('afterend',window.examTiming?.view(e)||'');
              }
              if(e?.state==='started'&&!e.waiting){const start=node.querySelector('[data-exam-timing-form] [name=scheduled_at]');if(start)start.disabled=true;}
            });
            return;
          }
          window.examConfig.render(next);
        }
      }else{
        const running=document.querySelector('.bridge-statistics .stat-card:last-child strong');if(running)running.textContent=next.stats.running_exams;
      }
      data=next;
    }catch(_){}finally{deadlinePolling=false;}
  }
  document.addEventListener('exam-window-opened',pollDeadlines);
  setInterval(pollDeadlines,5000);
})();
