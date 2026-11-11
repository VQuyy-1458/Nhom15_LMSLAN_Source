/* Server-authenticated LAN attendance; no camera or session selection. */
(() => {
  'use strict';
  function consumeLink(){
    if(location.pathname!=='/student/attendance')return;
    const url=new URL(location.href);
    if(url.searchParams.has('session')||url.searchParams.has('code')){url.searchParams.delete('session');url.searchParams.delete('code');history.replaceState(null,'',url.pathname+url.search);}
  }
  function scanner(){return '<section class="alert alert-info" data-lan-attendance-student><strong>Điểm danh qua LAN</strong><p>Giữ tài khoản đăng nhập và kết nối với server. Khi giảng viên mở điểm danh buổi học, hệ thống tự ghi nhận có mặt. Kết quả và các điều chỉnh của giảng viên hiển thị trong lịch sử bên dưới.</p></section>';}
  window.studentAttendance={scanner,consumeLink,stop(){},configure(){},active:()=>false};
})();
