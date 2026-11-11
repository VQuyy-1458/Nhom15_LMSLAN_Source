/* Interaction acceptance for UI.md; called by browser_ui_consistency.cjs. */
const assert=require('node:assert/strict');
module.exports=async({base,fixture,send,evaluate,waitFor,navigate})=>{
  const visibleH1="[...document.querySelectorAll('main h1')].filter(n=>n.getClientRects().length).length";
  async function cookie(role){await send('Network.clearBrowserCookies');await send('Network.setCookie',{name:'css_session',value:fixture[role],url:base,httpOnly:true,sameSite:'Strict'});}
  async function click(selector){const find=`[...document.querySelectorAll(${JSON.stringify(selector)})].find(n=>n.getClientRects().length)`;await waitFor(()=>evaluate(`!!(${find})`));await evaluate(`{const node=${find};node.focus();node.click();}`);}
  async function closed(){await waitFor(()=>evaluate("!document.querySelector('dialog[open]')"));}
  async function tab(key='Tab'){await send('Input.dispatchKeyEvent',{type:'keyDown',key,code:key,windowsVirtualKeyCode:key==='Tab'?9:27});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code:key});}
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
  await cookie('student');
  await navigate(base+'/student/dashboard');await waitFor(()=>evaluate("!!document.querySelector('#workspace-content .panel')"));
  assert.equal(await evaluate("!!document.querySelector('.student-hero,.page-intro-card')"),false);
  assert.equal(await evaluate(visibleH1),1);
  await navigate(base+`/student/assignments?course=${fixture.course}`);
  await waitFor(()=>evaluate("!!document.querySelector('[data-cl-filter=q]')"));
  await evaluate("{const input=document.querySelector('[data-cl-filter=q]');input.value='no-results-ui-check';input.dispatchEvent(new Event('input',{bubbles:true}));}");
  assert.equal(await evaluate("document.querySelectorAll('.cl-lines [data-learning-detail]').length"),0);
  await click('[data-cl-clear]');
  assert.equal(await evaluate("document.querySelector('[data-cl-filter=q]').value"),'');
  const openAssignment=await evaluate(`fetch('/api/student/workspace').then(r=>r.json()).then(d=>d.assignments.find(a=>a.course_id===${JSON.stringify(fixture.course)}&&!a.closed_at&&Date.parse(a.due_at)>Date.now()&&d.submissions.filter(s=>s.assignment_id===a.id).length<a.max_attempts)?.id)`);
  assert(openAssignment,'Fixture has no assignment accepting uploads');
  await click(`[data-learning-detail="assignment"][data-item="${openAssignment}"]`);
  await waitFor(()=>evaluate("!!document.querySelector('.ui-workspace[open]')"));
  assert.equal(await evaluate("!!document.querySelector('dialog:modal')"),false,'Assignment details must be an inline workspace');
  assert.equal(await evaluate(visibleH1),1);
  assert.equal(await evaluate("!!document.querySelector('.ui-workspace input[type=file]')"),true,'Upload control preserved');
  await click('[data-close-student-detail]');await closed();
  assert.equal(await evaluate(visibleH1),1);
  await navigate(base+`/student/courses?course=${fixture.course}&tab=materials`);
  await click('[data-learning-detail="material"]');
  await waitFor(()=>evaluate("!!document.querySelector('dialog:modal')"));
  for(let i=0;i<8;i++){await tab();assert.equal(await evaluate("document.querySelector('dialog:modal').contains(document.activeElement)"),true,'Modal focus escaped');}
  await tab('Escape');await closed();
  await cookie('admin');
  await navigate(base+'/admin/question-bank');
  await click('[data-bank-new]');await waitFor(()=>evaluate("!!document.querySelector('.ui-workspace [data-cl-form=question]')"));
  assert.equal(await evaluate(visibleH1),1);
  assert.equal(await evaluate("!!document.querySelector('dialog:modal')"),false);
  await evaluate("{const f=document.querySelector('[data-cl-form=question]');f.elements.title.value='Kiểm tra nháp chưa lưu';f.elements.title.dispatchEvent(new Event('input',{bubbles:true}));}");
  await click('[data-design-close]');await closed();
  await waitFor(()=>evaluate("document.activeElement.matches('[data-bank-new]')"));
  await click('[data-bank-tab=papers]');await click('[data-bank-new]');
  await waitFor(()=>evaluate("!!document.querySelector('.ui-workspace [data-paper-form]')"));
  await click('[data-design-close]');await closed();
  const fileQuestion=await evaluate("fetch('/api/admin/workspace').then(r=>r.json()).then(d=>d.question_bank.find(q=>q.response_type==='file'&&!q.archived)?.id)");
  if(fileQuestion){
    const title='UI workspace save '+Date.now();
    await click('[data-bank-new]');
    await evaluate(`{const form=document.querySelector('[data-paper-form]');form.elements.title.value=${JSON.stringify(title)};form.elements.response_type.value='file';form.elements.response_type.dispatchEvent(new Event('change',{bubbles:true}));form.querySelector('input[name=question_ids][value="${fileQuestion}"]').checked=true;form.requestSubmit();}`);
    await closed();
    const saved=await evaluate(`fetch('/api/admin/workspace').then(r=>r.json()).then(d=>d.question_papers.find(p=>p.title===${JSON.stringify(title)})?.id)`);
    assert(saved,'Workspace form did not persist through the existing API');
    await evaluate(`fetch('/api/admin/question-papers/archive',{method:'POST',body:new URLSearchParams({id:${JSON.stringify(saved)}})}).then(r=>{if(!r.ok)throw Error('Could not archive test draft')})`);
  }
  await navigate(base+'/admin?section=accounts');await click('#design-import-students');
  await waitFor(()=>evaluate("!!document.querySelector('dialog:modal #import-form')"));
  await tab('Escape');await closed();
  assert.equal(await evaluate("!!document.querySelector('#import-form')"),true,'Import form was lost after closing');
  await navigate(base+'/login');
  await evaluate("document.querySelector('form[action=\"/login\"]').requestSubmit()");
  assert.equal(await evaluate("!!document.querySelector('#username[aria-invalid=true]')"),true);
  assert.equal(await evaluate("!!document.querySelector('#username-error[role=alert]')?.textContent"),true);
  // At 200% zoom a 1440x900 desktop has a 720x450 CSS viewport. This is a
  // reflow check, not a claim of comprehensive screen-reader/WCAG compliance.
  await cookie('student');
  for(const [width,height] of [[1152,720],[960,600],[720,450]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
    await navigate(base+`/student/assignments?course=${fixture.course}`);
    await waitFor(()=>evaluate("!!document.querySelector('[data-cl-list]')"));
    assert.equal(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),true,`Zoom reflow overflow at ${width}`);
  }
  console.log('PASS: assignment and bank workspaces, preserved controls, unsaved-close confirmation, native modal focus/Escape/restore, import form lifecycle, inline errors and 125/150/200% desktop reflow');
};
