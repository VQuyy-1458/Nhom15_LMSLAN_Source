/* Server-authenticated LAN attendance; no camera or session selection. */
(() => {
  'use strict';
  function consumeLink(){
    if(location.pathname!=='/student/attendance')return;
    const url=new URL(location.href);
    if(url.searchParams.has('session')||url.searchParams.has('code')){url.searchParams.delete('session');url.searchParams.delete('code');history.replaceState(null,'',url.pathname+url.search);}
  }
  function scanner(){return '<section class="panel student-scan-panel" data-lan-attendance-student><div class="student-section-head"><div><h2>Điểm danh qua LAN</h2><p class="muted">Giữ tài khoản đăng nhập và kết nối với server. Khi giảng viên mở điểm danh buổi học, hệ thống tự ghi nhận có mặt. Kết quả và các điều chỉnh của giảng viên hiển thị trong lịch sử bên dưới.</p></div><span class="student-status blue"><i class="fa fa-check-square-o"></i> Tự động</span></div></section>';}
  window.studentAttendance={scanner,consumeLink,stop(){},configure(){},active:()=>false};
})();
