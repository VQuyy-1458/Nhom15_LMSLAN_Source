/* UI.md v2: measure layout and exercise the existing save APIs after grouping. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
module.exports=async({base,fixture,send,evaluate,waitFor,navigate})=>{
  async function click(selector){const find=`[...document.querySelectorAll(${JSON.stringify(selector)})].find(n=>n.getClientRects().length)`;await waitFor(()=>evaluate(`!!(${find})`));await evaluate(`{const n=${find};n.focus();n.click();}`);}
  async function close(){await click('[data-design-close]');await waitFor(()=>evaluate("!document.querySelector('dialog[open]')"));}
  async function dimensions(width){await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});}
  async function formCheck(profile){
    const report=await evaluate(`(()=>{const form=document.querySelector('form[data-ui-form="${profile}"]'),workspace=form.closest('dialog')||form.closest('.exam-setup')||form;return {width:workspace.getBoundingClientRect().width,groups:form.querySelectorAll('.ui-form-section').length,columns:[...form.querySelectorAll('.ui-form-section>.ui-form-grid')].map(g=>getComputedStyle(g).gridTemplateColumns.split(' ').length),actions:form.querySelectorAll('.ui-action-bar').length,actionLast:form.querySelector('.ui-action-bar')===((form.querySelector(':scope>fieldset.exam-form-fields,:scope>fieldset.code-participants-fields')||form).lastElementChild),primaries:form.querySelectorAll('.ui-action-bar .btn-primary').length,overflow:document.documentElement.scrollWidth>innerWidth+1};})()`);
    assert(report.width<=1121,JSON.stringify(report));assert(report.groups>0,JSON.stringify(report));
    assert(report.columns.every(n=>n===2),JSON.stringify(report));assert.equal(report.actions,1);assert(report.actionLast);assert.equal(report.primaries,1);assert(!report.overflow,JSON.stringify(report));
    assert.equal(await evaluate(`(()=>{for(const grid of document.querySelector('form[data-ui-form="${profile}"]').querySelectorAll('.ui-form-section>.ui-form-grid')){let track=0;for(const child of grid.children){if(!child.getClientRects().length)continue;if(getComputedStyle(child).gridColumnEnd==='-1'){if(track)return false;}else track=1-track;}if(track)return false;}return true;})()`),true,'Empty half-row in '+profile);
    assert.equal(await evaluate(`document.querySelector('form[data-ui-form="${profile}"]').querySelectorAll('fieldset:not(.exam-form-fields):not(.exam-problem):not(.ui-choice-group)').length`),0,'Unstyled choice fieldset in '+profile);
    const out=path.join(__dirname,'../previews/ui-contracts');fs.mkdirSync(out,{recursive:true});
    const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(path.join(out,profile+'-1280.png'),Buffer.from(shot.data,'base64'));
  }
  await send('Network.clearBrowserCookies');await send('Network.setCookie',{name:'css_session',value:fixture.admin,url:base,httpOnly:true,sameSite:'Strict'});
  await dimensions(1280);await navigate(base+'/admin/question-bank');await click('[data-bank-new]');
  await formCheck('question');
  await dimensions(1920);
  assert.equal(await evaluate("Math.round(document.querySelector('dialog.ui-form-workspace').getBoundingClientRect().width)"),1120,'Workspace must stop growing at 1120px');
  await dimensions(1280);
  const order=await evaluate("[...document.querySelector('form[data-ui-form=question]').elements].map(n=>n.name)");
  assert(order.includes('title')&&order.includes('course_id')&&order.includes('extensions'));
  await dimensions(1024);
  assert.equal(await evaluate("[...document.querySelectorAll('.ui-form-section>.ui-form-grid')].every(g=>getComputedStyle(g).gridTemplateColumns.split(' ').length===1)"),true);
  await dimensions(1280);await close();
  await click('[data-bank-tab=papers]');await click('[data-bank-new]');await formCheck('paper');
  assert.equal(await evaluate("!!document.querySelector('.ui-rule-details summary')"),true);await close();
  await navigate(base+'/admin/courses');await click('[data-course-create]');await formCheck('course');await close();
  await navigate(base+`/admin/courses?course=${fixture.course}&tab=assignment`);
  await waitFor(()=>evaluate("!!document.querySelector('form[data-ui-form=assignment][data-ui-prepared]')"));await formCheck('assignment');
  await navigate(base+`/admin/courses?course=${fixture.course}&tab=weekly`);await click('[data-week-edit]');await formCheck('week');await close();
  await navigate(base+`/admin/courses?course=${fixture.course}&tab=assignments`);await click('[data-practical-create]');await formCheck('practical');await close();
  await navigate(base+'/admin?section=exam');await click('[data-exam-create]');await formCheck('exam');
  assert.equal(await evaluate("document.querySelector('[name=course_id]').closest('label').textContent.includes('sở hữu')"),true);await close();
  await navigate(base+'/admin?section=exam&exam=current');
  await waitFor(()=>evaluate("!!document.querySelector('#settings-form[data-ui-prepared]')"));await formCheck('file-settings');
  if(await evaluate("!!document.querySelector('[data-ui-form=timing]')"))await formCheck('timing');
  const codeExam=await evaluate("fetch('/api/admin/workspace').then(r=>r.json()).then(d=>d.exams.find(e=>e.type==='programming'&&e.state==='idle')?.id)");
  if(codeExam){
    await navigate(base+'/admin?section=exam&exam='+codeExam);
    await waitFor(()=>evaluate("!!document.querySelector('[data-ui-form=participants][data-ui-prepared]')"));
    await formCheck('exam');await formCheck('participants');
    await waitFor(()=>evaluate("!!document.querySelector('.exam-problem.ui-form-grid')"));
    assert.equal(await evaluate("[...document.querySelectorAll('.exam-problem[hidden]')].every(n=>!n.getClientRects().length)"),true,'Hidden editor was exposed by grid CSS');
  }
  // The grouping helper must preserve successful controls and their listeners,
  // including the disabled exam fieldset's original scope.
  const preserved=await evaluate(`(()=>{const f=document.createElement('form');f.dataset.uiForm='exam';f.innerHTML='<input name="id" type="hidden" value="sample"><fieldset class="exam-form-fields"><div class="two-cols"><label>A<input name="title" value="A"></label><label>B<select name="assessment_type"><option value="test">Test</option></select></label></div><label>D<textarea name="description">text</textarea></label><fieldset><legend>Choice</legend><label><input type="checkbox" name="paper_ids" value="paper" checked>Paper</label></fieldset><button>Save</button></fieldset>';const title=f.elements.title;let changed=false;title.addEventListener('change',()=>changed=true);const before=[...new FormData(f)];window.uiForms.prepareAll(f);const after=[...new FormData(f)];title.dispatchEvent(new Event('change'));f.querySelector('.exam-form-fields').disabled=true;return {before,after,changed,same:before.length===after.length,disabled:[...new FormData(f)]};})()`);
  assert.deepEqual(preserved.after,preserved.before);assert(preserved.changed);assert.deepEqual(preserved.disabled,[['id','sample']]);
  // Real save from the reorganized course form; subsequent tests retain the
  // fixture course and use a uniquely named, separate test record.
  await navigate(base+'/admin/courses');await click('[data-course-create]');
  const code='UIC'+Date.now();
  await evaluate(`{const f=document.querySelector('[data-ui-form=course]');f.elements.name.value='UI contract course';f.elements.code.value=${JSON.stringify(code)};f.elements.semester.value='Học kỳ kiểm thử';f.requestSubmit();}`);
  await waitFor(()=>evaluate("!document.querySelector('dialog[open]')"));
  assert.equal(await evaluate(`fetch('/api/admin/workspace').then(r=>r.json()).then(d=>d.courses.some(c=>c.code===${JSON.stringify(code)}))`),true);
  console.log('PASS: UI.md contracts on question/paper/course/assignment/week/practical/exam forms; 1120px limit, two columns at 1280, one at 1024, action bars, FormData/listener/disabled preservation and real course save');
};
