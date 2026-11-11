/* UI.md form contracts. Builders opt in with data-ui-form. Moving existing
   controls preserves their names, values, listeners and FormData semantics. */
(() => {
  'use strict';
  const policies={
    question:[['Thông tin',['title','purpose','response_type','week_number','source_url']],['Phạm vi luyện tập',['course_ids']],['Nội dung',['statement','extensions'],'[data-code-question],[data-file-question]']],
    paper:[['Thông tin',['title','response_type']],['Nội dung đề',['description','question_ids'],'[data-paper-search]']],
    week:[['Thông tin',['week_number','title']],['Nội dung',['lesson_text','reading_text']],['Học liệu và hoạt động',['material_ids','assignment_ids','activity_ids','announcement_ids']]],
    practical:[['Thông tin',['title','response_type','duration_minutes','week_number']],['Nội dung',['description'],'[data-practical-questions]'],['Thí sinh',['student_ids']]],
    exam:[['Thông tin kỳ thi',['course_id','assessment_type','title','scheduled_at','duration_minutes','type']],['Nội dung đề',['description','paper_ids','paper_distribution','questions_per_student','language'],'[data-paper-picker],.exam-programming'],['Chính sách nộp',['accepted_submission_extensions','submission_policy','max_submissions','overwrite_previous']]],
    participants:[['Danh sách dự thi',['student_ids'],'[data-code-participant-list]']],
    timing:[['Thời gian thi',['scheduled_at','mode','duration_minutes','ends_at']]],
    'file-settings':[['Chính sách nộp',['exam_duration_minutes','submission_policy','max_submissions','overwrite_previous','accepted_submission_extensions']],['Truy cập đề',['exam_password_enabled','exam_password']]],
    course:[['Thông tin',['name','code','group','semester']],['Nội dung',['description']],['Thành viên ban đầu',['student_ids','include_previous']]],
    assignment:[['Thông tin',['title','topic','week_number','category','short_code']],['Nội dung',['description','file']],['Chính sách nộp',['due_at','max_attempts']]],
    material:[['Thông tin',['title','topic','week_number']],['Tài liệu',['description','file']]],
    event:[['Thông tin',['title','kind','starts_at','location']],['Nội dung',['description']]],
    trial:[['Chấm thử',['language','source']]]
  };
  const controls='input,select,textarea';
  function named(node){return [...(node.matches(controls)?[node]:[]),...node.querySelectorAll(controls)].map(el=>el.name).filter(Boolean);}
  function wide(node){return !node.matches('label,.ui-field')||!!node.querySelector('textarea,input[type=file],fieldset');}
  function choice(group){
    for(const fieldset of group.querySelectorAll('fieldset:not(.exam-form-fields):not(.exam-problem)'))fieldset.classList.add('ui-choice-group');
  }
  function balance(grid){
    // A final unpaired short field spans both tracks; leave no empty half-row.
    let track=0;
    let previous;
    for(const node of grid.children){
      node.classList.remove('ui-balanced-span');
      if(node.classList.contains('ui-span-2')){if(track===1&&previous)previous.classList.add('ui-balanced-span');track=0;}else track=1-track;
      previous=node;
    }
    const last=grid.lastElementChild;
    if(last&&track===1)last.classList.add('ui-balanced-span');
  }
  function prepare(form){
    if(form.dataset.uiPrepared)return;
    const profile=form.dataset.uiForm,policy=policies[profile];if(!policy)return;
    form.dataset.uiPrepared='true';form.classList.add('ui-form-workspace');
    const host=form.querySelector(':scope > fieldset.exam-form-fields,:scope > fieldset.code-participants-fields')||form;
    // Flatten layout wrappers only, never the editor, roster or choice groups.
    for(const wrapper of [...host.children].filter(n=>n.matches('.two-cols,.cl-filters,.course-create-grid,.assignment-config-grid'))){wrapper.replaceWith(...wrapper.childNodes);}
    // Legacy settings use external for/id labels. Keep that relationship and
    // its live input, but make the pair a single grid item.
    for(const label of [...host.children].filter(n=>n.matches('label[for]')&&!n.querySelector(controls))){
      const input=form.querySelector('#'+CSS.escape(label.htmlFor));
      if(input?.parentElement===host){const field=document.createElement('div');field.className='ui-field';label.before(field);field.append(label,input);}
    }
    for(const field of host.children)if(field.matches('div')&&field.querySelectorAll('label').length===1&&field.querySelectorAll('input:not([type=hidden]),select,textarea').length===1&&!field.querySelector('button,fieldset'))field.classList.add('ui-field');
    const groups=policy.map(([title])=>{
      const section=document.createElement('section');section.className='ui-form-section';
      const heading=document.createElement('h3');heading.textContent=title;
      const grid=document.createElement('div');grid.className='ui-form-grid';section.append(heading,grid);
      return {section,grid};
    });
    const action=document.createElement('div');action.className='ui-action-bar';
    const feedback=[],hidden=[];
    let previous=0;
    for(const node of [...host.children]){
      if(node.matches('input[type=hidden]')){hidden.push(node);continue;}
      if(node.matches('[role=alert],[role=status],.ref-form-error')){feedback.push(node);continue;}
      if(node.matches('button:not([type]),button[type=submit]')||node.querySelector('button:not([type]),button[type=submit]')&&!node.querySelector(controls)&&node.matches('.ref-actions,.form-actions,.bridge-inline,div:not([class])')){
        if(node.matches('button'))action.append(node);else action.append(...node.childNodes);continue;
      }
      const names=named(node);
      let index=policy.findIndex(([,fields,selector])=>(selector&&(node.matches(selector)||node.querySelector(selector)))||names.some(name=>fields.includes(name)));
      if(index<0)index=previous;previous=index;
      if(wide(node))node.classList.add('ui-span-2');
      groups[index].grid.append(node);
    }
    host.replaceChildren(...hidden);
    for(const {section,grid} of groups)if(grid.children.length){balance(grid);choice(section);host.append(section);}
    for(const node of feedback){node.classList.add('ui-span-2');host.append(node);}
    if(action.children.length){const primary=action.querySelector(':scope>.btn-primary');if(primary)action.append(primary);host.append(action);}
    // No control is disabled or removed here: backend scoping and form
    // validation continue to use exactly the original successful controls.
  }
  function prepareAll(root){
    if(root.matches?.('form[data-ui-form]'))prepare(root);
    for(const form of root.querySelectorAll?.('form[data-ui-form]')||[])prepare(form);
    choice(root);
    const problems=[...(root.matches?.('.exam-problem')?[root]:[]),...(root.querySelectorAll?.('.exam-problem')||[])];
    for(const problem of problems){
      problem.classList.add('ui-form-grid');
      for(const child of problem.children)if(wide(child))child.classList.add('ui-span-2');
      balance(problem);
      for(const limits of problem.querySelectorAll('.exam-limits'))limits.classList.add('ui-form-grid');
    }
  }
  window.uiForms={prepareAll};
})();
