const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const handlers={};
const context={window:{cssEscape:value=>String(value??'').replaceAll('<','&lt;')},document:{addEventListener(type,fn){(handlers[type]||=[]).push(fn);},getElementById(){return null;},querySelector(){return null;}},addEventListener(){}};
vm.createContext(context);vm.runInContext(fs.readFileSync('static/js/classification-ui.js','utf8'),context);
const ui=context.window.classificationUI;
ui.setCatalog({topics:[{id:'t1',name:'Loops',active:true},{id:'t2',name:'<Arrays>',active:false}]});
const rows=[
  {id:'a',content_type:'assignment',topic_ids:['t1','t2'],difficulty:'hard',classification_languages:['python']},
  {id:'e',content_type:'exam',topic_ids:['t1'],difficulty:'easy',classification_languages:[],programming:{languages:['cpp']}},
  {id:'q',content_type:'question',topic_ids:['t2'],difficulty:'hard',classification_languages:['python']}
];
function choose(criterion,value,id='test'){
  const select={dataset:{classificationFilter:id,criterion},value};
  for(const fn of handlers.change)fn({target:{closest(){return select;}}});
}
const ids=id=>Array.from(ui.filter(rows,id||'test').items,r=>r.id);
assert.deepEqual(ids(),['a','e','q']);
choose('topic','t1');assert.deepEqual(ids(),['a','e']);
choose('difficulty','hard');assert.deepEqual(ids(),['a']);
choose('language','cpp');assert.deepEqual(ids(),[]);
choose('difficulty','');assert.deepEqual(ids(),['e']); // Falls back to actual configured languages.
choose('kind','assignment');assert.deepEqual(ids(),[]);
assert.deepEqual(ids('another'),['a','e','q']);
assert(!ui.fields({}).includes('value="t2"')); // Archived topics cannot be newly selected.
assert(ui.fields(rows[0]).includes('value="t2"')); // Existing references remain editable.
assert(ui.badges(rows[0]).includes('&lt;Arrays>'));
console.log('PASS: taxonomy topic/difficulty/language/type filters, isolated list state, archived references and escaping.');
