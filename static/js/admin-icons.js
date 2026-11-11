/* One local Font Awesome vocabulary for both roles (UI.md). */
(() => {
  'use strict';
  const aliases={'dashboard':'th-large','calendar-o':'calendar','cloud-upload':'upload','cloud-download':'download','angle-right':'chevron-right','angle-left':'chevron-left'};
  function decorate(node){
    const icons=[...(node.matches?.('i.fa')?[node]:[]),...(node.querySelectorAll?.('i.fa')||[])];
    for(const icon of icons){
      if(icon.dataset.designIcon){delete icon.dataset.designIcon;icon.replaceChildren();}
      for(const [oldName,name] of Object.entries(aliases))if(icon.classList.contains('fa-'+oldName)){icon.classList.remove('fa-'+oldName);icon.classList.add('fa-'+name);}
      icon.setAttribute('aria-hidden','true');
    }
  }
  window.classroomAdminIcons={decorate};
})();
