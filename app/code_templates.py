"""Build isolated test programs. Templates are data, never evaluated on the host."""
import re

ANSWER = '{{ STUDENT_ANSWER }}'
TEST = '{{ TEST.testcode }}'


def validate(problem):
    kind = problem.get('answer_kind', 'program')
    if kind not in {'program', 'class', 'method'}:
        raise ValueError('Dạng bài phải là program, class hoặc method.')
    template = problem.get('template', '')
    if not isinstance(template, str) or len(template) > 100000:
        raise ValueError('Template không hợp lệ hoặc quá dài.')
    if template and (ANSWER not in template or TEST not in template):
        raise ValueError('Template cần chứa {{ STUDENT_ANSWER }} và {{ TEST.testcode }}.')
    for test in problem.get('tests', []):
        code = test.get('test_code', '')
        if not isinstance(code, str) or len(code) > 100000:
            raise ValueError('Test code không hợp lệ hoặc quá dài.')
        if kind != 'program' and not code.strip():
            raise ValueError('Bài class/method cần mã kiểm thử cho mỗi test.')
        if kind == 'program' and code.strip() and not template:
            raise ValueError('Program có test code cần template tùy chỉnh.')
        if test.get('feedback_visibility', 'sample') not in {'sample', 'show', 'hide', 'hide_if_fail', 'hide_if_succeed'}:
            raise ValueError('Chính sách phản hồi test không hợp lệ.')


def build(source, language, problem, test):
    answer = source.decode('utf-8-sig')
    code = test.get('test_code', '')
    template = problem.get('template', '')
    kind = problem.get('answer_kind', 'program')
    extras = {}
    if not template and kind == 'program':
        return source, extras
    if not template:
        if language == 'java':
            if kind == 'class':
                # Preserve public classes in correctly named files, without rewriting source.
                match = re.search(r'\bpublic\s+(?:(?:final|abstract)\s+)?class\s+([A-Za-z_$][\w$]*)', answer)
                name = match.group(1) if match else 'Submission'
                if name == 'Main' or re.search(r'^\s*package\s+', answer, re.M):
                    raise ValueError('Bài class dùng tên lớp theo đề, không dùng Main hoặc package.')
                extras[name + '.java'] = source
                template = 'public class Main { public static void main(String[] args) throws Exception { '+TEST+' } }'
            else:
                template = 'public class Main { '+ANSWER+' public static void main(String[] args) throws Exception { new Main().runTests(); } void runTests() throws Exception { '+TEST+' } }'
        elif language == 'python':
            template = ANSWER+'\n'+TEST+'\n'
        elif language == 'cpp':
            template = '#include <bits/stdc++.h>\nusing namespace std;\n'+ANSWER+'\nint main(){\n'+TEST+'\n}\n'
        elif language == 'c' and kind == 'method':
            template = '#include <stdio.h>\n#include <stdlib.h>\n'+ANSWER+'\nint main(void){\n'+TEST+'\n}\n'
        else:
            raise ValueError('Ngôn ngữ không hỗ trợ dạng bài này.')
    # Single substitution pass: markers inside submitted code are never interpreted.
    rendered = re.sub(r'\{\{ STUDENT_ANSWER \}\}|\{\{ TEST\.testcode \}\}', lambda m: answer if m.group() == ANSWER else code, template)
    return rendered.encode('utf-8'), extras


def visible(test):
    policy = test.get('feedback_visibility', 'sample')
    return policy == 'show' or (policy == 'sample' and test.get('sample', False)) or (policy == 'hide_if_fail' and test.get('verdict') == 'AC') or (policy == 'hide_if_succeed' and test.get('verdict') != 'AC')
