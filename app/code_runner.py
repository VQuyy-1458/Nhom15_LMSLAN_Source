"""Compile and run only inside disposable, restricted Linux containers."""
import os
import logging
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
import json
import re
from datetime import datetime
from pathlib import Path

from .config import BASE_DIR, RUNTIME_DIR

IMAGE = os.getenv("CSS_JUDGE_IMAGE", "classroom-judge:1")
WORK = RUNTIME_DIR / "judge-work"
LANGUAGES = {"c": "main.c", "cpp": "main.cpp", "java": "Main.java", "python": "main.py"}
logger = logging.getLogger(__name__)
MAX_JOB_SECONDS = 300
_last_status = None
_ready_lock = threading.Lock()


def docker():
    executable = shutil.which("docker")
    if not executable:
        raise RuntimeError("Chưa có Docker để chạy bộ chấm.")
    return executable


def _inspect_status():
    global _last_status
    try:
        result = subprocess.run([docker(), "image", "inspect", IMAGE], capture_output=True, timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode == 0:
            rows = json.loads(result.stdout)
            detail = {"ready":True, "detail":"Bộ chấm đã sẵn sàng.", "image_id":rows[0]["Id"], "image":IMAGE}
            _last_status = (time.monotonic(), IMAGE, detail)
            return detail
        error = result.stderr.decode("utf-8", "replace").lower()
        detail = "Thiếu image bộ chấm. Cần thiết lập bộ chấm trước khi mở thi." if "no such image" in error else "Không kết nối được bộ chấm. Hãy mở Docker Desktop và chờ khởi động xong."
        return {"ready": False, "detail": detail}
    except RuntimeError:
        return {"ready": False, "detail": "Chưa cài Docker để chạy bộ chấm."}
    except (OSError, subprocess.TimeoutExpired):
        return {"ready": False, "detail": "Bộ chấm không phản hồi. Hãy kiểm tra hoặc khởi động lại Docker Desktop."}
    except (ValueError, KeyError, IndexError, AttributeError):
        return {"ready":False, "detail":"Không đọc được thông tin image bộ chấm. Hãy kiểm tra lại Docker."}


def status():
    global _last_status
    detail = _inspect_status()
    _last_status = (time.monotonic(), IMAGE, detail)
    return detail


def ready():
    if _last_status and _last_status[1] == IMAGE and time.monotonic()-_last_status[0] < 2:
        return _last_status[2]["ready"]
    with _ready_lock:
        if _last_status and _last_status[1] == IMAGE and time.monotonic()-_last_status[0] < 2:
            return _last_status[2]["ready"]
        return status()["ready"]


def image_identity():
    return _last_status[2].get("image_id", IMAGE) if _last_status and _last_status[1] == IMAGE else IMAGE


def budget_valid(problem):
    from .oop_rubric import tests as rubric_tests
    return (len(problem["tests"]) + len(rubric_tests(problem.get("oop_rubric")))) * (problem["time_limit_ms"]/1000 + 1) <= MAX_JOB_SECONDS-30


def test_weights(problem):
    """Give each structural criterion its stated score; share the rest among manual cases."""
    from .oop_rubric import tests as rubric_tests
    tests = rubric_tests(problem.get("oop_rubric")) + problem["tests"]
    if not tests or len(tests) > 100:
        raise ValueError('Cần từ 1 đến 100 tiêu chí/test case cho một bài.')
    explicit, unset = 0.0, []
    weights = []
    for index, test in enumerate(tests):
        value = test.get('points', '')
        if value in ('', None):
            weights.append(None); unset.append(index)
        else:
            try: weight = float(value)
            except (ValueError, TypeError) as exc: raise ValueError('Điểm test case không hợp lệ.') from exc
            if not 0 < weight <= problem['points'] or round(weight, 2) != weight:
                raise ValueError('Điểm test case phải dương và tối đa 2 chữ số thập phân.')
            weights.append(weight); explicit += weight
    remaining = round(problem['points'] - explicit, 2)
    if remaining < 0 or (unset and remaining <= 0) or (not unset and remaining != 0):
        raise ValueError('Tổng điểm tiêu chí và test case phải bằng điểm tối đa của bài.')
    for index in unset:
        weights[index] = remaining / len(unset)
    return tests, weights


def _remove_container(name):
    try:
        subprocess.run([docker(), "rm", "-f", name], capture_output=True, timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (RuntimeError, OSError, subprocess.TimeoutExpired):
        # A stalled daemon must not replace a completed verdict or mask the
        # original infrastructure failure with a cleanup exception.
        logger.warning("Could not remove judge container %s", name, exc_info=True)


def matches(actual, expected, checker):
    if checker=='json':
        def object_value(pairs):
            result={}
            for key,value in pairs:
                if key in result:raise ValueError('duplicate key')
                result[key]=value
            return result
        def invalid_constant(value):raise ValueError(value)
        def equal(a,b):
            if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
            if isinstance(a,dict) and isinstance(b,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
            if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
            return (type(a) is type(b) or isinstance(a,(int,float)) and isinstance(b,(int,float))) and a==b
        try:return equal(json.loads(actual,object_pairs_hook=object_value,parse_constant=invalid_constant),json.loads(expected,object_pairs_hook=object_value,parse_constant=invalid_constant))
        except (ValueError,TypeError,RecursionError):return False
    # Normalize OS line endings; exact mode preserves spaces and final newlines.
    actual, expected = actual.replace("\r\n", "\n"), expected.replace("\r\n", "\n")
    return actual.split() == expected.split() if checker == "tokens" else actual == expected


def _container(folder, command, *, memory, timeout, input_data=b"", readonly=True, image=None):
    name = "css-judge-" + uuid.uuid4().hex
    mount = f"type=bind,source={folder.resolve()},target=/work" + (",readonly" if readonly else "")
    # Reserve timeout's exit statuses by normalizing all child failures to 1.
    wrapped = ["sh", "-c", '"$@"; code=$?; if [ "$code" -ne 0 ]; then exit 1; fi', "judge-child", *command]
    args = [docker(), "run", "--pull=never", "--name", name, "--network=none", "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user=65534:65534", "--cpus=1", f"--memory={memory}m", f"--memory-swap={memory}m", "--pids-limit=64", "--ulimit", "fsize=67108864:67108864", "--ulimit", "nofile=64:64", "--tmpfs", "/tmp:rw,noexec,nosuid,size=32m", "--log-driver=none", "--mount", mount, "--workdir=/work", "-i", image or IMAGE, "timeout", "--signal=TERM", "--kill-after=0.1s", f"{timeout:.3f}s", *wrapped]
    output, errors = bytearray(), bytearray()
    overflow = threading.Event()
    process = None
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    def read(pipe, buffer, limit):
        try:
            while chunk := pipe.read(8192):
                available = max(0, limit - len(buffer))
                buffer.extend(chunk[:available])
                if len(chunk) > available:
                    overflow.set()
        except (OSError, ValueError):
            pass
    try:
        # stdin is a host temporary file outside the mounted source directory.
        with tempfile.TemporaryFile() as stdin:
            stdin.write(input_data); stdin.seek(0)
            process = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags)
            threads = [threading.Thread(target=read, args=(process.stdout, output, 1048576), daemon=True), threading.Thread(target=read, args=(process.stderr, errors, 65536), daemon=True)]
            for thread in threads: thread.start()
            end = time.monotonic() + timeout + 15
            while process.poll() is None and not overflow.is_set() and time.monotonic() < end:
                time.sleep(.02)
            infrastructure_timeout = process.poll() is None and not overflow.is_set()
            if process.poll() is None:
                _remove_container(name)
                process.kill()
            process.wait(timeout=5)
            for thread in threads: thread.join(timeout=2)
            inspect = subprocess.run([docker(), "inspect", "--format", "{{json .State}}", name], capture_output=True, timeout=5, creationflags=flags)
            import json
            state = json.loads(inspect.stdout) if inspect.returncode == 0 else {}
            duration = None
            if state.get("StartedAt") and state.get("FinishedAt"):
                try: duration = max(0, round((datetime.fromisoformat(state["FinishedAt"].replace("Z", "+00:00")) - datetime.fromisoformat(state["StartedAt"].replace("Z", "+00:00"))).total_seconds() * 1000))
                except ValueError: pass
            timed_out = process.returncode == 124 or (process.returncode in {137,143} and duration is not None and duration >= timeout*1000)
            return {"exit": process.returncode, "timed_out":timed_out, "stdout": output.decode("utf-8", "replace"), "stderr": errors.decode("utf-8", "replace"), "overflow": overflow.is_set(), "oom": state.get("OOMKilled", False), "time_ms": duration, "system_error": infrastructure_timeout or bool(state.get("Error")) or not state and not overflow.is_set()}
    finally:
        if process and process.poll() is None: process.kill()
        if process:
            process.stdout.close(); process.stderr.close()
        _remove_container(name)


def judge(source, language, problem, progress=None, image=None):
    from .code_templates import build, validate
    validate(problem)
    tests, weights = test_weights(problem)
    bundled = {}
    if language == 'java' and problem.get('accept_java_zip') and source.startswith(b'PK'):
        from .java_sources import submission
        source, bundled = submission(source, problem['oop_rubric']['class_name'])
    from .java_sources import teacher_files
    provided = teacher_files(problem.get('provided_files'), (problem.get('oop_rubric') or {}).get('class_name',''))
    for item in provided:
        if item['filename'].lower() in {name.lower() for name in bundled}:
            raise ValueError('File Java trong bài nộp trùng file giảng viên cung cấp.')
        bundled[item['filename']] = item['source'].encode('utf-8')
    if problem.get('answer_kind', 'program') == 'program' and not problem.get('template') and not problem.get('oop_rubric'):
        result = _judge_program(source, language, problem, progress, image)
        for row, test, weight in zip(result['tests'], tests, weights):
            row.update(criterion=test.get('criterion') or f'Test {row["index"]}',
                       category=test.get('category','behavior'),points=weight,
                       earned=weight if row['verdict']=='AC' else 0)
        if result['tests']:
            result['score'] = round(sum(row['earned'] for row in result['tests']),2)
        return result
    results = []
    started = time.monotonic()
    total = len(tests)
    if not total or total > 100 or not budget_valid(problem):
        raise ValueError('Cấu hình test không hợp lệ.')
    compiled_source = False
    for index, test in enumerate(tests):
        if time.monotonic() - started > MAX_JOB_SECONDS:
            raise RuntimeError('Lượt chấm vượt thời gian xử lý tổng.')
        try:
            if problem.get('answer_kind') == 'program' and test.get('category') == 'structure':
                # The reflection probe supplies its own Main; keep the submitted
                # entry point under a different name for this structural check.
                probe_source = re.sub(rb'\bMain\b', b'__SubmittedMain', source) if language == 'java' else source
                generated, extras = build(probe_source, language, dict(problem, answer_kind='class', template=''), test)
            else:
                generated, extras = build(source, language, problem, test)
            if any(name.lower() in {extra.lower() for extra in extras} for name in bundled):
                raise ValueError('Tên file Java trùng với lớp chính của bài nộp.')
            extras.update(bundled)
        except (ValueError, UnicodeError) as exc:
            return {'verdict':'CE','score':0,'passed':0,'total':total,'compile_log':str(exc),'tests':[]}
        if progress: progress('judging', index, total)
        one = dict(problem, tests=[test], oop_rubric=None)
        result = _judge_program(generated, language, one, image=image, extra_sources=extras)
        if result['verdict'] == 'CE':
            # Compiler diagnostics can contain private test code from the wrapper.
            result['private_compile_log'] = result['compile_log']
            result['compile_log'] = 'Không biên dịch được bài làm với mã kiểm thử. Kiểm tra tên lớp, constructor và chữ ký phương thức.'
            if not compiled_source:
                result['total'] = total
                return result
            # A later teacher test may reference a missing student member.
            # The source compiled in an earlier reflection test: only this criterion fails.
            results.append({'index':index+1,'sample':test['sample'],'verdict':'WA','time_ms':0,
                            'input':test['input'],'expected':test['output'],'actual':'',
                            'stderr':'','test_code':test.get('test_code',''),
                            'private_compile_log':result['private_compile_log'],
                            'criterion':test.get('criterion') or f'Test {index+1}', 'category':test.get('category','behavior'),
                            'points':weights[index],'earned':0,
                            'feedback_visibility':test.get('feedback_visibility','sample')})
            continue
        compiled_source = True
        row = result['tests'][0]
        row.update(index=index+1, test_code=test.get('test_code',''),
                   criterion=test.get('criterion') or f'Test {index+1}',category=test.get('category','behavior'),
                   points=weights[index],earned=weights[index] if row['verdict']=='AC' else 0)
        results.append(row)
    passed = sum(t['verdict']=='AC' for t in results)
    if progress: progress('judging', total, total)
    return {'verdict':'AC' if passed==total else next(t['verdict'] for t in results if t['verdict']!='AC'), 'score':round(sum(t['earned'] for t in results),2),'passed':passed,'total':total,'compile_log':'','tests':results}


def java_public_class(source):
    """Find the top-level public type, ignoring comments and string literals."""
    clean = re.sub(rb'"""[\s\S]*?"""|//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', b' ', source)
    depth, public, type_name = 0, False, False
    for token in re.findall(rb'[A-Za-z_$][\w$]*|[{};]', clean):
        if depth == 0:
            if type_name:
                return token.decode('ascii')
            if token == b'public':
                public = True
            elif public and token in {b'class', b'record', b'enum'}:
                type_name = True
            elif token == b';':
                public = False
        if token == b'{':
            depth += 1
        elif token == b'}':
            depth -= 1
            if depth == 0:
                public = False
    return 'Main'


def _judge_program(source, language, problem, progress=None, image=None, extra_sources=None):
    if language not in LANGUAGES:
        raise ValueError("Ngôn ngữ không hợp lệ.")
    if not ready():
        raise RuntimeError("Docker hoặc image classroom-judge:1 chưa sẵn sàng.")
    if not problem.get("tests") or not budget_valid(problem):
        raise ValueError("Cấu hình test vượt ngân sách chấm hoặc không có test.")
    image = image or image_identity()
    WORK.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="job-", dir=WORK) as directory:
        folder = Path(directory)
        folder.chmod(0o777)
        java_entry = 'Main'
        java_filename = 'Main.java'
        if language == 'java':
            # A complete Java program may use any public entry class, e.g. J05005.
            from .code_templates import java_package
            java_class = java_public_class(source)
            java_filename = java_class + '.java'
            try:
                package = java_package(source.decode('utf-8-sig', 'replace'))
            except ValueError as exc:
                return {"verdict":"CE","score":0,"passed":0,"total":len(problem["tests"]),"compile_log":str(exc),"tests":[]}
            java_entry = package + '.' + java_class if package else java_class
        filename = java_filename if language == 'java' else LANGUAGES[language]
        (folder / filename).write_bytes(source.removeprefix(b"\xef\xbb\xbf"))
        for name, content in (extra_sources or {}).items():
            (folder / name).write_bytes(content.removeprefix(b'\xef\xbb\xbf'))
        compile_command = {"c": ["gcc", "-std=c17", "-O2", filename, "-o", "program"], "cpp": ["g++", "-std=c++17", "-O2", filename, "-o", "program"], "java": ["javac", "-J-Xmx256m", "-J-XX:ActiveProcessorCount=1", "-proc:none", "-d", ".", filename]}.get(language)
        if language == 'java' and extra_sources:
            compile_command.extend(sorted(extra_sources))
        if compile_command:
            if progress: progress("compiling", 0, len(problem["tests"]))
            compiled = _container(folder, compile_command, memory=768, timeout=20, readonly=False, image=image)
            if compiled["system_error"]: raise RuntimeError("Môi trường biên dịch không sẵn sàng.")
            if compiled["exit"] or compiled["overflow"]:
                return {"verdict": "CE", "score": 0, "passed": 0, "total": len(problem["tests"]), "compile_log": (compiled["stderr"] or compiled["stdout"])[:16000], "tests": []}
        memory = problem["memory_limit_mb"]
        run_command = {"c": ["./program"], "cpp": ["./program"], "java": ["java", f"-Xmx{max(8, memory-64)}m", "-XX:ActiveProcessorCount=1", "-XX:+UseSerialGC", "-XX:ReservedCodeCacheSize=16m", java_entry], "python": ["python3", "-I", "-B", "main.py"]}[language]
        results = []
        if progress: progress("judging", 0, len(problem["tests"]))
        deadline = time.monotonic() + MAX_JOB_SECONDS
        for index, test in enumerate(problem["tests"]):
            if time.monotonic() > deadline: raise RuntimeError("Lượt chấm vượt thời gian xử lý tổng, hãy giảm số test hoặc thời lượng mỗi test.")
            run = _container(folder, run_command, memory=memory, timeout=problem["time_limit_ms"] / 1000, input_data=test["input"].encode("utf-8"), image=image)
            if run["system_error"]: raise RuntimeError("Không thể khởi chạy môi trường chấm.")
            verdict = "OLE" if run["overflow"] else "MLE" if run["oom"] else "TLE" if run.get("timed_out", False) else "RE" if run["exit"] else "AC" if matches(run["stdout"], test["output"], problem["checker"]) else "WA"
            results.append({"index": index+1, "sample": test["sample"], "verdict": verdict, "time_ms": run["time_ms"], "input": test["input"], "expected": test["output"], "actual": run["stdout"][:16000], "stderr": run["stderr"][:4000]})
            if progress: progress("judging", index+1, len(problem["tests"]))
            results[-1]['feedback_visibility'] = test.get('feedback_visibility', 'sample')
        passed = sum(t["verdict"] == "AC" for t in results)
        return {"verdict": "AC" if passed == len(results) else next(t["verdict"] for t in results if t["verdict"] != "AC"), "score": round(problem["points"] * passed / len(results), 2), "passed": passed, "total": len(results), "tests": results, "compile_log": ""}
