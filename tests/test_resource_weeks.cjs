const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const handlers={};
const document={addEventListener(name,fn){handlers[name]=fn;},querySelectorAll(){return [];}};
const context={document,window:{cssEscape:v=>String(v??'').replaceAll('<','&lt;'),classroomActivities:{kind:v=>v},listUi:{view:(_,rows)=>rows,controls:()=>''}}};
vm.createContext(context);
for(const name of ['resource-weeks','admin-courses-design','student-workspace'])vm.runInContext(fs.readFileSync(`static/js/${name}.js`,'utf8'),context);
const api=context.window.resourceWeeks;
const data={courses:[{id:'c',name:'Course'}],events:[
  {id:'first',course_id:'c',kind:'lesson',starts_at:'2026-11-02T00:00:00Z'},
  {id:'second',course_id:'c',kind:'lesson',starts_at:'2026-11-08T17:00:00Z'},
  {id:'other',course_id:'other',kind:'lesson',starts_at:'2026-11-10T00:00:00Z'}
],session_contents:[{event_id:'second',material_id:'linked',assignment_id:'task'},{event_id:'other',material_id:'unknown'}],materials:[
  {id:'linked',course_id:'c',title:'Linked material',original_filename:'notes.pdf'},
  {id:'topic',course_id:'c',title:'Explicit topic',topic:'Tuần 03: Introduction'},
  {id:'unknown',course_id:'c',title:'Unknown material',topic:'Chủ đề 02',created_at:'2026-11-10T00:00:00Z'}
],assignments:[{id:'task',course_id:'c',title:'Task',description:'<unsafe>',due_at:'2026-12-01T00:00:00Z',original_filename:'task.pdf'}],submissions:[]};
const plain=value=>JSON.parse(JSON.stringify(value));
assert.deepEqual(plain(api.weeks(data,data.materials[0],'materials')),[2]);
assert.deepEqual(plain(api.weeks(data,data.materials[1],'materials')),[3]);
assert.deepEqual(plain(api.weeks(data,data.materials[2],'materials')),[]);
assert.deepEqual(plain(api.weeks(data,{course_id:'c',id:'x',topic:'Week 4 / tuần #5'},'materials')),[4,5]);
assert.deepEqual(plain(api.weeks(data,{course_id:'c',id:'x',topic:'Week 0 / Week 2abc'},'materials')),[]);
let changes=0;api.onChange(()=>changes++);
function select(id,value){handlers.change({target:{closest:()=>({dataset:{resourceWeekFilter:id},value})}});}
let view=api.prepare(data,data.materials,'materials','test');
assert.equal(view.entries.length,3);
select('test','unassigned');view=api.prepare(data,data.materials,'materials','test');
assert.deepEqual(plain(view.entries.map(e=>e.row.id)),['unknown']);
select('test','2');view=api.prepare(data,data.materials,'materials','test');
assert.deepEqual(plain(view.entries.map(e=>e.row.id)),['linked']);assert.equal(changes,2);
assert.equal(api.prepare(data,data.materials,'materials','another').entries.length,3);
const options={scope:'c',filters:{q:'',course:'',status:''},page:1};
for(const type of ['materials','assignments']){
  const student=context.window.studentWorkspace[type](data,options);
  const teacher=context.window.courseDesign.teaching(data,{id:'c',status:'active'},type);
  for(const html of [student,teacher]){
    assert(html.includes('<details class="resource-line'));
    assert(html.includes('data-resource-week-filter'));
    assert(html.includes(`/api/learning/preview/${type}/`));
    assert(html.includes(`/api/learning/files/${type}/`));
  }
  if(type==='assignments'){
    assert(student.includes('data-learning-detail="assignment"'));
    assert(teacher.includes('section=submissions'));
    assert(student.includes('&lt;unsafe>'));assert(!student.includes('<unsafe>'));
  }
}
console.log('Resource weeks: explicit topics, lesson links, no date guessing, filters, compact rows and actions passed.');
