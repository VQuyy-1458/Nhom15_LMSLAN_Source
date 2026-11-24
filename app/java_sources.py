"""Small, flat Java source bundles for OOP submissions and teacher dependencies."""
import io
import re
import zipfile


NAME = re.compile(r'[A-Za-z_$][\w$]*\.java\Z')
MAX_ARCHIVE = 300000
MAX_FILES = 20
MAX_SOURCE = 100000
MAX_TOTAL = 250000


def teacher_files(value, class_name=''):
    if value in (None, ''):
        return []
    if not isinstance(value, list) or len(value) > 10:
        raise ValueError('Tối đa 10 file Java do giảng viên cung cấp.')
    rows, names = [], {'Main.java', class_name + '.java'}
    for item in value:
        if not isinstance(item, dict):
            raise ValueError('File Java cung cấp không hợp lệ.')
        name, source = item.get('filename'), item.get('source')
        if not isinstance(name, str) or not NAME.fullmatch(name) or name.lower() in {n.lower() for n in names}:
            raise ValueError('Tên file Java cung cấp không hợp lệ hoặc trùng tên.')
        if not isinstance(source, str) or not source.strip() or len(source.encode('utf-8')) > MAX_SOURCE:
            raise ValueError('Nội dung file Java cung cấp không hợp lệ hoặc quá lớn.')
        names.add(name)
        rows.append({'filename':name,'source':source})
    if sum(len(row['source'].encode('utf-8')) for row in rows) > MAX_TOTAL:
        raise ValueError('Tổng dung lượng file Java cung cấp quá lớn.')
    return rows


def submission(source, class_name):
    if not 0 < len(source) <= MAX_ARCHIVE or not zipfile.is_zipfile(io.BytesIO(source)):
        raise ValueError('Bài nộp ZIP không hợp lệ hoặc quá lớn.')
    files, total = {}, 0
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        entries = archive.infolist()
        if not 1 <= len(entries) <= MAX_FILES:
            raise ValueError('ZIP cần từ 1 đến 20 file Java.')
        for entry in entries:
            name = entry.filename
            if entry.is_dir() or not NAME.fullmatch(name) or name.lower() in {n.lower() for n in files} or name == 'Main.java':
                raise ValueError('ZIP chỉ nhận file .java ở thư mục gốc, không trùng tên và không chứa Main.java.')
            if entry.file_size > MAX_SOURCE or entry.flag_bits & 1:
                raise ValueError('File Java trong ZIP quá lớn hoặc đã mã hóa.')
            total += entry.file_size
            if total > MAX_TOTAL:
                raise ValueError('Tổng mã nguồn trong ZIP vượt 250 KB.')
            content = archive.read(entry)
            if len(content) != entry.file_size:
                raise ValueError('ZIP chứa file lỗi.')
            try: content.decode('utf-8-sig')
            except UnicodeDecodeError as exc: raise ValueError('File Java trong ZIP phải dùng UTF-8.') from exc
            files[name] = content
    target = class_name + '.java'
    if target not in files:
        raise ValueError(f'ZIP cần chứa {target}.')
    return files.pop(target), files
