const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
for(const [template,consumer] of [['admin','admin-courses-design'],['student','student-workspace']]){
  const html=fs.readFileSync(`templates/${template}.html`,'utf8');
  const dependency=html.indexOf('/static/js/resource-weeks.js');
  assert(dependency>=0,`${template} must load resource-weeks.js`);
  assert(dependency<html.indexOf(`/static/js/${consumer}.js`),`${template} must load week helpers before consumers`);
  assert(html.includes('/static/css/resource-weeks.css'),`${template} must load compact list styles`);
}
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
vm.runInContext(fs.readFileSync('static/js/programming-assignments.js','utf8'),context);
data.programming_assignments=[
  {id:'pa_official',course_id:'c',title:'Official code homework',topic:'Week 2',due_at:'2026-12-01T00:00:00Z',state:'started',participants:['s1'],programming:{problems:[{}],languages:['python']}},
  {id:'pa_draft',course_id:'c',title:'Draft code homework',due_at:'2026-12-01T00:00:00Z',state:'idle',participants:[],programming:{problems:[{}],languages:['python']}},
  {id:'pa_other',course_id:'other',title:'Other course code homework',state:'started'}
];
const course={id:'c',status:'active'};
let combined=context.window.courseDesign.teaching(data,course,'assignments');
assert(combined.includes('data-assignment-list'));
assert(combined.includes('data-pa-published="pa_official"'));
assert.equal((combined.match(/data-pa-published="pa_official"/g)||[]).length,1);
assert(combined.includes('section=submissions'));
assert(combined.includes('data-pa-results="pa_official"'));
assert(!combined.includes('Draft code homework'));assert(!combined.includes('Other course code homework'));
const drafts=context.window.programmingAssignmentsUI.adminList(data,course);
assert(drafts.includes('Draft code homework'));assert(!drafts.includes('Official code homework'));assert(!drafts.includes('data-pa-official'));
select('course:assignments:c','unassigned');
combined=context.window.courseDesign.teaching(data,course,'assignments');
assert(!combined.includes('Official code homework'));
select('course:assignments:c','2');
combined=context.window.courseDesign.teaching(data,course,'assignments');assert(combined.includes('Official code homework'));
console.log('Unified homework list: published code/file assignments share week filters; drafts and other courses excluded.');
data.programming={exams:[
  {id:'pa_student',course_id:'c',activity_type:'assignment',state:'started',title:'Student code homework',topic:'Week 3',due_at:'2099-12-01T00:00:00Z',languages:['python'],can_start:true},
  {id:'pa_hidden_draft',course_id:'c',activity_type:'assignment',state:'idle',title:'Student draft'},
  {id:'exam_only',course_id:'c',activity_type:'exam',state:'started',title:'Separate exam'},
  {id:'pa_foreign',course_id:'other',activity_type:'assignment',state:'started',title:'Foreign homework',languages:['java']}
],submissions:[]};
let studentCombined=context.window.studentWorkspace.assignments(data,options);
assert(studentCombined.includes('data-student-assignment-list'));
assert(studentCombined.includes('data-learning-detail="assignment"'));
assert.equal((studentCombined.match(/data-programming-assignment="pa_student"/g)||[]).length,1);
assert.equal((studentCombined.match(/data-resource-week-filter=/g)||[]).length,1);
assert(studentCombined.includes('tab=assignments&exam=pa_student'));
for(const text of ['Student draft','Separate exam','Foreign homework'])assert(!studentCombined.includes(text));
select('student:assignments:c','2');
studentCombined=context.window.studentWorkspace.assignments(data,options);
assert(!studentCombined.includes('Student code homework'));assert(studentCombined.includes('data-learning-detail="assignment"'));
select('student:assignments:c','3');
studentCombined=context.window.studentWorkspace.assignments(data,options);
assert(studentCombined.includes('Student code homework'));assert(!studentCombined.includes('data-learning-detail="assignment"'));
select('student:assignments:c','all');
studentCombined=context.window.studentWorkspace.assignments(data,{...options,filters:{...options.filters,status:'submitted'}});
assert(!studentCombined.includes('Student code homework'));
data.programming.submissions.push({exam_id:'pa_student'});
studentCombined=context.window.studentWorkspace.assignments(data,{...options,filters:{...options.filters,status:'submitted'}});
assert(studentCombined.includes('Student code homework'));
console.log('Student unified list: one week filter, file/code actions, course isolation, drafts excluded and submit status passed.');
