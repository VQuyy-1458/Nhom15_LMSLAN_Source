"""Export the current synthetic trial dataset without machine credentials or sessions."""
import copy
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from app import storage, learning, programming
    from app.security import hash_password
    from app.maintenance import roots, reference_issues
    storage.initialize()
    with learning.LOCK, storage.transaction():
        documents = {name: storage.read_json(name) for name in storage.document_names()}
    marker = documents.get('demo_seed.json', {})
    if marker.get('version') != 'four-courses-7-weeks-v1':
        raise RuntimeError('Only export the synthetic four-course dataset.')
    for name in ('sessions.json', 'login_attempts.json', 'auth_throttle.json', 'machines.json', 'submission_rate.json'):
        documents[name] = {}
    documents['admins.json'] = {'admin': {'password_hash': hash_password('111111'), 'full_name': 'Quản trị viên', 'active': True}}
    for student in documents['students.json'].values():
        student.update(password_hash=hash_password('111111'), last_ip=None, last_seen=None)
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items() if key not in {'ip', 'last_ip', 'ip_at_assignment', 'backup', 'applied_at', 'device_id', 'session_id'}}
        if isinstance(value, list): return [clean(item) for item in value]
        return value
    documents = clean(documents)
    issues = reference_issues(roots(), documents)
    if issues: raise RuntimeError(str(issues))
    target = ROOT / 'sample-data' / 'lan-lms-data.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, value in documents.items():
            archive.writestr('data/' + name, json.dumps(value, ensure_ascii=False, indent=2))
        for category, folder in roots().items():
            if category == 'data': continue
            for path in folder.rglob('*'):
                if path.is_file() and path.resolve().is_relative_to(folder.resolve()) and not path.is_symlink():
                    archive.write(path, category + '/' + path.relative_to(folder).as_posix())
        for path in (ROOT / 'demo-inputs').glob('*'):
            if path.is_file(): archive.write(path, 'demo-inputs/' + path.name)
    print(f'Exported {target} ({target.stat().st_size} bytes)')


if __name__ == '__main__': main()
