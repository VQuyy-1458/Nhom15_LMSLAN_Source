/* Audit every main screen and course tab using disposable fixture data.
   Run: node tests/browser_ui_consistency.cjs; screenshots: previews/ui-consistency. */
const {spawn}=require('node:child_process'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),profile=fs.mkdtempSync(path.join(os.tmpdir(),'classroom-login-'));
let app,browser,socket,id=1;const callbacks=new Map(),requests=[],responses=[],jsErrors=[];
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function waitFor(fn,ms=15000){const end=Date.now()+ms;while(Date.now()<end){try{if(await fn())return;}catch(_){}await delay(100);}throw new Error('Timed out');}
function ready(proc,stream,pattern){return new Promise((resolve,reject)=>{let out='';const timer=setTimeout(()=>reject(new Error('Readiness timeout')),20000);proc[stream].on('data',chunk=>{out+=chunk;const match=out.match(pattern);if(match){clearTimeout(timer);resolve(match[1]);}});proc.once('exit',code=>reject(new Error(`Process exited ${code}: ${out.slice(-1000)}`)));});}
function send(method,params={}){return new Promise((resolve,reject)=>{const key=id++;const timer=setTimeout(()=>reject(new Error('CDP timeout: '+method)),15000);callbacks.set(key,{resolve:v=>{clearTimeout(timer);resolve(v)},reject:e=>{clearTimeout(timer);reject(e)}});socket.send(JSON.stringify({id:key,method,params}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.text);return r.result.value;}
async function navigate(url){const prior=await evaluate('performance.timeOrigin');await send('Page.navigate',{url});await waitFor(()=>evaluate(`performance.timeOrigin!==${prior} && document.readyState==='complete'`));}
async function login(username='QA001'){await waitFor(()=>evaluate("!!document.querySelector('#username')"));await evaluate(`document.querySelector('#username').value=${JSON.stringify(username)};document.querySelector('#password').value='qa-password';document.querySelector('form[action="/login"]').requestSubmit();`);}
(async()=>{
  const {python,chrome}=require('./test_environment.cjs');
  app=spawn(python,['-u',path.join(__dirname,process.argv.includes('--system-data')?'serve_system_test_qa.py':'serve_student_qa.py')],{cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe']});
  const fixture=JSON.parse(await ready(app,'stdout',/QA_READY ([^\r\n]+)/));
  browser=spawn(chrome,['--headless=new','--no-sandbox','--disable-extensions','--disable-gpu','--no-first-run','--no-proxy-server','--host-resolver-rules=MAP classroom.test 127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
  const ws=await ready(browser,'stderr',/DevTools listening on (ws:\/\/[^\r\n]+)/),port=new URL(ws).port;
  const target=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  socket=new WebSocket(target.webSocketDebuggerUrl);await new Promise(r=>socket.addEventListener('open',r,{once:true}));
  socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true});if(m.method==='Runtime.exceptionThrown')jsErrors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.id){const c=callbacks.get(m.id);if(c){callbacks.delete(m.id);m.error?c.reject(new Error(JSON.stringify(m.error))):c.resolve(m.result);}}if(m.method==='Network.requestWillBeSent'&&m.params.request.method==='POST')requests.push({url:m.params.request.url,headers:m.params.request.headers});if(m.method==='Network.responseReceived')responses.push({url:m.params.response.url,status:m.params.response.status});});
  await send('Page.enable');await send('Runtime.enable');await send('Network.enable');

  console.log('Browser ready');
  app.stderr.on('data',()=>{});
  const base=`http://127.0.0.1:${fixture.port}`;
  const phase=process.argv.includes('--desktop')?'desktop':process.argv.includes('--quick')?'quick':'after';
  const out=path.join(root,'previews',process.argv.includes('--system-data')?'system-data':'ui-consistency',phase);fs.mkdirSync(out,{recursive:true});
  const results=[];
  for(const role of ['student','admin']){
    await send('Network.clearBrowserCookies');
    await send('Network.setCookie',{name:'css_session',value:fixture[role],url:base,httpOnly:true,sameSite:'Strict'});
    const routes=role==='student'?['dashboard','courses','calendar','attendance','assignments','exams','history','grades','notifications','profile',...['weekly','materials','assignments','calendar','exams','grades'].map(tab=>'courses?course='+fixture.course+'&tab='+tab)]:['dashboard','courses','monitor','notifications','bank','exam','accounts','submissions','server','admins'];
    if(role==='admin')routes.push(...['overview','materials','assignments','calendar','members','grades'].map(tab=>'courses?course='+fixture.course+'&tab='+tab));
    for(const width of (process.argv.includes('--quick')?[1440]:process.argv.includes('--desktop')?[1280,1366,1440,1920,1024]:[1440,1024,768,390])){
      const height=process.argv.includes('--desktop')?({1280:720,1366:768,1440:900,1920:1080,1024:768})[width]:1000;
      await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
      for(const view of (process.argv.includes('--quick')?['dashboard','courses','notifications']:routes)){
        const route=role==='student'?'/student/'+view:view.startsWith('courses')?'/admin/'+view:view==='bank'?'/admin/question-bank':'/admin?section='+view;
        await navigate(base+route);
        await waitFor(()=>evaluate("!document.querySelector('.student-loading') && !!document.querySelector('main h1')"));await delay(350);
        const state=await evaluate("(()=>{const s=getComputedStyle(document.querySelector('.main-sidebar'));return {overflow:document.documentElement.scrollWidth>innerWidth+1,headings:[...document.querySelectorAll('main h1')].filter(e=>e.getClientRects().length).length,sidebar:s.display,actionsRight:document.querySelector('.topbar-actions').getBoundingClientRect().right,errors:document.querySelector('#workspace-error,#admin-workspace-error')?.textContent||''};})()");
        results.push({role,view,width,...state});
        if((width===1440||width===390)&&['dashboard','courses','accounts','notifications','profile','monitor'].includes(view)){
          const shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(out,`${role}-${view}-${width}.png`),Buffer.from(shot.data,'base64'));
        }
      }
    }
  }
  assert.deepEqual(jsErrors,[],'Browser JavaScript exceptions');
  if(process.argv.includes('--standard'))await require('./ui_standard_interactions.cjs')({base,fixture,send,evaluate,waitFor,navigate});
  if(process.argv.includes('--contracts'))await require('./ui_contract_interactions.cjs')({base,fixture,send,evaluate,waitFor,navigate});
  assert.deepEqual(jsErrors,[],'Browser JavaScript exceptions during interactions');
  fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify(results,null,2));
  const failures=results.filter(r=>r.overflow||r.headings!==1||r.errors||r.actionsRight>r.width);
  console.log(JSON.stringify({phase,screens:results.length,failures},null,2));
  assert.equal(failures.length,0,'UI layout audit failed');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{socket?.close();browser?.kill();app?.kill();});
