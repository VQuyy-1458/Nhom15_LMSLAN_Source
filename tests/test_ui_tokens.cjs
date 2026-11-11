/* Check the actual foreground/background pairs defined by UI.md components. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const css=fs.readFileSync(path.join(__dirname,'../static/css/design-system.css'),'utf8');
const token=name=>{const match=css.match(new RegExp('--ui-'+name+':(#[0-9a-f]{3,6})[;}]'));assert(match,'Missing token '+name);return match[1];};
function luminance(hex){if(hex.length===4)hex='#'+[...hex.slice(1)].map(v=>v+v).join('');const rgb=hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;}
function contrast(a,b){const values=[luminance(a),luminance(b)].sort((a,b)=>b-a);return (values[0]+.05)/(values[1]+.05);}
for(const [name,bg] of [['text',token('surface')],['text-muted',token('surface')],['text-muted',token('surface-soft')],['success-text','#eaf6ef'],['warning-text','#fff5df'],['danger','#ffefed']])assert(contrast(token(name),bg)>=4.5,`${name} on ${bg}`);
for(const name of ['primary','primary-hover','success','danger'])assert(contrast('#fff',token(name))>=4.5,`Button/toast ${name}`);
assert(contrast(token('control-border'),token('surface'))>=3,'Control boundary contrast');
console.log('PASS: semantic text, muted text, status labels, buttons/toasts and control boundary contrast');
