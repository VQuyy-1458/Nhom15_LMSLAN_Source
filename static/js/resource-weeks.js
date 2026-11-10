/* Week labels come only from explicit topics or linked course lessons. */
(() => {
  'use strict';
  const esc=window.cssEscape, selections=new Map(), listeners=[];
  const monday=value=>{
    const key=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Ho_Chi_Minh',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(value));
    const day=new Date(key+'T12:00:00Z');
    return Date.parse(key+'T00:00:00+07:00')-((day.getUTCDay()+6)%7)*86400000;
  };
  function weeks(data,row,type){
    const result=new Set();
    for(const match of String(row.topic||'').matchAll(/(?:^|[^\p{L}\p{N}])(?:tuần|week)\s*(?:[:#-]\s*)?(\d+)(?![\p{L}\p{N}])/giu)){
      const n=Number(match[1]);if(Number.isSafeInteger(n)&&n>0)result.add(n);
    }
    const lessons=(data.events||[]).filter(e=>e.course_id===row.course_id&&e.kind==='lesson'&&Number.isFinite(Date.parse(e.starts_at)));
    const first=lessons.length?Math.min(...lessons.map(e=>monday(e.starts_at))):null;
    if(first!==null)for(const content of data.session_contents||[]){
      if(content[type==='materials'?'material_id':'assignment_id']!==row.id)continue;
      const lesson=lessons.find(e=>e.id===content.event_id);
      if(lesson)result.add(Math.floor((monday(lesson.starts_at)-first)/(7*86400000))+1);
    }
    return [...result].sort((a,b)=>a-b);
  }
  function prepare(data,items,type,id){
    const entries=items.map(row=>({row,weeks:weeks(data,row,type)}));
    const available=[...new Set(entries.flatMap(e=>e.weeks))].sort((a,b)=>a-b);
    let selected=selections.get(id)||'all';
    if(selected!=='all'&&selected!=='unassigned'&&!available.includes(Number(selected)))selected='all';
    const controls=`<div class="resource-week-filter"><label>Lọc theo tuần<select data-resource-week-filter="${esc(id)}"><option value="all" ${selected==='all'?'selected':''}>Tất cả các tuần</option>${available.map(n=>`<option value="${n}" ${selected===String(n)?'selected':''}>Tuần ${n}</option>`).join('')}<option value="unassigned" ${selected==='unassigned'?'selected':''}>Chưa gắn tuần</option></select></label></div>`;
    return {controls,entries:entries.filter(e=>selected==='all'||(selected==='unassigned'?!e.weeks.length:e.weeks.includes(Number(selected)))),selected};
  }
  function grouped(entries,render,selected='all'){
    const keys=selected==='all'?[...new Set(entries.flatMap(e=>e.weeks))].sort((a,b)=>a-b):selected==='unassigned'?[]:[Number(selected)];
    if((selected==='all'||selected==='unassigned')&&entries.some(e=>!e.weeks.length))keys.push('unassigned');
    return keys.map(key=>`<section class="resource-week-group"><h3>${key==='unassigned'?'Chưa gắn tuần':'Tuần '+key}</h3><div class="resource-lines">${entries.filter(e=>key==='unassigned'?!e.weeks.length:e.weeks.includes(key)).map(e=>render(e.row)).join('')}</div></section>`).join('')||'<p class="muted resource-empty">Không có nội dung phù hợp.</p>';
  }
  document.addEventListener('change',event=>{
    const select=event.target.closest('[data-resource-week-filter]');if(!select)return;
    selections.set(select.dataset.resourceWeekFilter,select.value);
    listeners.forEach(fn=>fn());
    [...document.querySelectorAll('[data-resource-week-filter]')].find(el=>el.dataset.resourceWeekFilter===select.dataset.resourceWeekFilter)?.focus({preventScroll:true});
  });
  window.resourceWeeks={weeks,prepare,grouped,onChange(fn){listeners.push(fn);}};
})();
