/* Reusable paper selection and random code-paper configuration. */
(() => {
  'use strict';
  const esc=window.cssEscape;
  function fields(e={}){return `<fieldset data-paper-distribution><legend>Phân phối bộ câu hỏi code</legend><div class="two-cols"><label>Cách giao bộ câu<select name="paper_distribution"><option value="common" ${e.paper_distribution!=='random'?'selected':''}>Cùng bộ câu cho cả lớp</option><option value="random" ${e.paper_distribution==='random'?'selected':''}>Ngẫu nhiên bộ câu riêng cho từng sinh viên</option></select></label><label>Số câu mỗi sinh viên (khi chọn ngẫu nhiên)<input type="number" name="questions_per_student" min="1" max="30" value="${e.questions_per_student||1}"></label></div><p class="muted">Mỗi người nhận một tập con từ các câu trong đề. Bộ câu được lưu cố định lúc phân phối, không đổi khi tải lại trang. Điểm quy đổi theo tổng điểm tối đa của bộ được giao.</p></fieldset>`;}
  async function picker(form){
    const root=form.querySelector('[data-paper-picker]');
    try{
      const data=await window.cssRequest('/api/admin/classification');if(!root.isConnected)return;
      const papers=(data.papers||[]).filter(p=>p.published);
      root.innerHTML=`<label>Chọn đề thi độc lập đã lưu<select name="blueprint_id"><option value="">Tự chọn câu từ ngân hàng / Tạo đề mới</option>${papers.map(p=>`<option value="${p.id}" data-format="${p.response_type}">${esc(p.title)} · ${p.response_type==='code'?'Code':'Nộp file'} · ${p.question_ids.length} câu</option>`).join('')}</select></label><p class="muted">Quản lý đề dùng lại tại Phân loại & phân quyền → Đề thi độc lập. Mỗi kỳ thi sao chép nội dung riêng; lịch và danh sách dự thi không làm thay đổi đề gốc.</p>`;
      root.querySelector('select').addEventListener('change',()=>{const option=form.elements.blueprint_id.selectedOptions[0];if(option.value)form.elements.type.value=option.dataset.format==='file'?'file':'programming';sync(form);});
    }catch(error){root.textContent=error.message;}
  }
  function sync(form){
    const code=form.elements.type.value==='programming',blueprint=!!form.elements.blueprint_id?.value;
    const bank=form.querySelector('[data-exam-bank]');if(bank){bank.hidden=!code||blueprint;bank.querySelectorAll('[data-bank-question]').forEach(n=>{if(!n.hasAttribute('data-bank-existing'))n.disabled=blueprint;});}
    const config=form.querySelector('[data-paper-distribution]');if(config){config.hidden=!code;config.disabled=!code;}
  }
  function fileControls(e){
    if(e.type!=='file'||!e.generated_exam_file)return '';
    return `<section class="panel"><h2>Phân phối đề nộp file từ ngân hàng</h2><p>Đề đã được tạo từ các câu hỏi trong đề thi độc lập. Sinh viên làm và nộp file, giảng viên chấm điểm theo luồng hiện có.</p><label>Danh sách MSSV (để trống để giao toàn bộ sinh viên đang hoạt động trong lớp)<textarea data-file-paper-students rows="3"></textarea></label><div class="bridge-inline">${e.state==='idle'?`<button type="button" class="btn btn-primary" data-file-paper-control="distribute" data-exam="${e.id}">Phân phối đề</button>`:e.state==='distributed'?`<button type="button" class="btn btn-primary" data-file-paper-control="start" data-exam="${e.id}">Mở kỳ thi</button>`:e.state==='started'?`<button type="button" class="btn btn-danger" data-file-paper-control="end" data-exam="${e.id}">Kết thúc kỳ thi</button>`:'<p>Đã kết thúc.</p>'}</div></section>`;
  }
  document.addEventListener('click',async event=>{
    const button=event.target.closest('[data-file-paper-control]');if(!button)return;button.disabled=true;
    try{
      if(button.dataset.filePaperControl==='distribute'){
        const form=document.querySelector('#exam-config-form');if(!form.reportValidity())return;
        await window.cssRequest('/api/admin/exam-configurations/save',{method:'POST',body:window.examConfig.payload(form)});window.examConfig.ackSaved(form);
      }
      await window.cssRequest('/api/admin/papers/file-control',{method:'POST',body:new URLSearchParams({exam_id:button.dataset.exam,action:button.dataset.filePaperControl,student_ids:button.closest('section').querySelector('[data-file-paper-students]').value})});location.reload();
    }catch(error){window.cssToast(error.message,'error');}finally{button.disabled=false;}
  });
  window.examPaperUI={fields,picker,sync,fileControls};
})();
