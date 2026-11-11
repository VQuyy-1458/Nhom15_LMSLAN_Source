/* Server-authenticated LAN attendance; no camera or session selection. */
(() => {
  'use strict';
  function consumeLink(){
    if(location.pathname!=='/student/attendance')return;
    const url=new URL(location.href);
    if(url.searchParams.has('session')||url.searchParams.has('code')){url.searchParams.delete('session');url.searchParams.delete('code');history.replaceState(null,'',url.pathname+url.search);}
  }
  function scanner(){return '';}
  window.studentAttendance={scanner,consumeLink,stop(){},configure(){},active:()=>false};
})();
