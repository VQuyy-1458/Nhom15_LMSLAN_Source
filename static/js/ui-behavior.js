/* Presentation-only behavior shared by both roles: accessible surfaces, local
   icons, field feedback and focus. Business requests remain in feature code. */
(() => {
  'use strict';
  const workspaces=new Set(),restorers=new Map();
  const longForms='form[data-ui-form],[data-paper-form],[data-cl-form="question"],[data-cl-form="week"],[data-cl-form="practical"],[data-trial-form],#exam-config-form';
  function open(node,{workspace=!!node.querySelector(longForms)}={}){
    window.uiForms.prepareAll(node);
    const opener=document.activeElement,hidden=[];
    node.dataset.uiDirty='false';
    node.addEventListener('input',()=>node.dataset.uiDirty='true');
    node.addEventListener('change',()=>node.dataset.uiDirty='true');
    if(workspace){
      const main=document.querySelector('main');
      // A non-modal native dialog retains .close()/close-event contracts used
      // by existing forms, while participating in normal page layout.
      // Keep a builder's original parent: course forms delegate submit to
      // #learning-content. Moving them outside it would bypass that handler.
      if(!main.contains(node))main.append(node);
      node.classList.add('ui-workspace','ui-form-workspace');node.setAttribute('role','region');
      const heading=node.querySelector('.ref-dialog-head h2,.cl-heading h2,.student-detail-head h2');
      if(heading){const h=document.createElement('h1');h.textContent=heading.textContent;heading.replaceWith(h);}
      let branch=node;
      while(branch!==main){
        for(const sibling of branch.parentElement.children){if(sibling===branch||sibling.matches('script,style,link'))continue;hidden.push([sibling,sibling.hidden,sibling.classList.contains('hidden')]);sibling.hidden=true;sibling.classList.add('hidden');}
        branch=branch.parentElement;
      }
      node.setAttribute('open','');workspaces.add(node);
      node.scrollIntoView({block:'start'});
      const headingNode=node.querySelector('h1');headingNode?.setAttribute('tabindex','-1');headingNode?.focus();
    }else{
      node.showModal();
      if(!node.dataset.uiFocusTrap)node.addEventListener('keydown',event=>{
        if(event.key!=='Tab')return;
        const controls=[...node.querySelectorAll('button,a[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(el=>!el.disabled&&el.getClientRects().length);
        if(!controls.length){event.preventDefault();return;}
        const current=controls.indexOf(document.activeElement),next=(current+(event.shiftKey?-1:1)+controls.length)%controls.length;
        event.preventDefault();controls[next].focus();
      });
      node.dataset.uiFocusTrap='true';
    }
    const mayClose=()=>node.dataset.uiDirty!=='true'||window.confirm('Bạn có thay đổi chưa lưu. Bỏ thay đổi và đóng?');
    node.addEventListener('cancel',event=>{if(!mayClose())event.preventDefault();});
    node.addEventListener('click',event=>{
      if(!event.target.closest('[data-design-close],[data-cl-close],[data-close-student-detail],button[value="cancel"]'))return;
      if(!mayClose()){event.preventDefault();event.stopImmediatePropagation();}
    },true);
    let restored=false;
    const restore=()=>{
      if(restored)return;restored=true;workspaces.delete(node);restorers.delete(node);
      for(const [el,prior,hadClass] of hidden)if(el.isConnected){el.hidden=prior;if(!hadClass)el.classList.remove('hidden');}
      if(opener?.isConnected)opener.focus();else document.querySelector('main h1')?.focus();
    };
    if(workspace)restorers.set(node,restore);
    node.addEventListener('close',restore,{once:true});
    return node;
  }
  window.uiSurfaces={open};
  window.addEventListener('beforeunload',event=>{if([...workspaces].some(n=>n.isConnected&&n.dataset.uiDirty==='true')){event.preventDefault();event.returnValue='';}});
  let fieldId=0;
  document.addEventListener('invalid',event=>{
    const input=event.target;if(!input.matches('input,select,textarea'))return;
    input.setAttribute('aria-invalid','true');
    if(!input.id)input.id='ui-field-'+(++fieldId);
    const id=input.id+'-error';let feedback=document.getElementById(id);
    if(!feedback){feedback=document.createElement('span');feedback.id=id;feedback.className='ui-field-error';feedback.setAttribute('role','alert');input.after(feedback);}
    feedback.textContent=input.validationMessage;
    input.setAttribute('aria-describedby',[...(input.getAttribute('aria-describedby')||'').split(' ').filter(Boolean),id].filter((v,i,a)=>a.indexOf(v)===i).join(' '));
  },true);
  document.addEventListener('input',event=>{
    const input=event.target;if(!input.matches('input,select,textarea')||!input.validity.valid)return;
    input.removeAttribute('aria-invalid');const error=document.getElementById(input.id+'-error');if(error)error.textContent='';
  });
  document.addEventListener('change',event=>{
    const input=event.target;if(!input.matches('input[type=file]'))return;
    let info=input.parentElement.querySelector('[data-ui-file-info]');
    if(!info){info=document.createElement('p');info.dataset.uiFileInfo='';info.className='muted';info.setAttribute('role','status');input.after(info);}
    info.textContent=[...input.files].map(f=>`${f.name} · ${(f.size/1024).toFixed(1)} KB`).join(', ');
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'){
      const workspace=[...workspaces].find(n=>n.isConnected);
      if(workspace&&event.target.closest('.ui-workspace')&&!document.querySelector('dialog:modal')){
        if(workspace.dataset.uiDirty!=='true'||window.confirm('Bạn có thay đổi chưa lưu. Bỏ thay đổi và đóng?'))workspace.close();
      }
    }
  });
  function decorate(root){
    window.uiForms.prepareAll(root);
    window.classroomAdminIcons?.decorate(root);
    for(const icon of root.querySelectorAll?.('i.fa')||[])icon.setAttribute('aria-hidden','true');
    for(const link of root.querySelectorAll?.('.sidebar-nav a')||[]){if(link.classList.contains('active'))link.setAttribute('aria-current','page');}
    for(const button of root.querySelectorAll?.('button[data-tab],button[data-bank-tab]')||[])button.setAttribute('aria-pressed',String(button.classList.contains('active')));
    for(const button of root.querySelectorAll?.('button[title]')||[])if(!button.textContent.trim()&&!button.getAttribute('aria-label'))button.setAttribute('aria-label',button.title);
    for(const time of root.querySelectorAll?.('time[datetime]')||[]){const value=Date.parse(time.dateTime);if(Number.isFinite(value))time.textContent=new Date(value).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'});}
  }
  document.addEventListener('DOMContentLoaded',()=>{
    decorate(document.body);
    new MutationObserver(records=>{
      for(const record of records)for(const node of record.addedNodes)if(node.nodeType===1)decorate(node);
      for(const node of workspaces)if(!node.isConnected)restorers.get(node)?.();
    }).observe(document.body,{childList:true,subtree:true});
  });
  document.addEventListener('ui-notification-sent',event=>{
    const list=document.getElementById('sent-notifications');if(!list)return;
    list.querySelector('[data-sent-empty]')?.remove();
    const li=document.createElement('li'),body=document.createElement('div'),message=document.createElement('p'),meta=document.createElement('p');
    message.textContent=event.detail.message;meta.className='muted';meta.textContent=`Vừa gửi · ${event.detail.recipientCount} sinh viên`;
    body.append(message,meta);li.append(body);list.prepend(li);
  });
})();
