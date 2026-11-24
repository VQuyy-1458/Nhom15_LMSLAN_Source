"""Validate Java OOP criteria and turn structural requirements into judge tests."""
import json
import re


IDENT = re.compile(r"[A-Za-z_$][\w$]*\Z")
QUALIFIED = re.compile(r"[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*\Z")
TYPES = re.compile(r"(?:[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*|void)(?:\[\])*\Z")
ACCESS = {"public", "protected", "private", "package"}


def _identifier(value, label, pattern=IDENT):
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"{label} không hợp lệ.")
    return value


def validate(value, points, language, kind):
    if not value:
        return None
    if language != "java" or kind not in {"class", "program"} or not isinstance(value, dict) or value.get("version") != 1:
        raise ValueError("Tiêu chí OOP phiên bản 1 chỉ hỗ trợ bài Java dạng class hoặc program.")
    name = _identifier(value.get("class_name"), "Tên lớp")
    if name == 'Main':
        raise ValueError('Bài class OOP cần tên lớp khác Main để chừa lớp kiểm thử.')
    package = value.get("package", "")
    if package:
        _identifier(package, "Package", QUALIFIED)
    criteria = value.get("criteria", [])
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= 60:
        raise ValueError("Cần khai báo từ 1 đến 60 tiêu chí OOP.")
    cleaned, total = [], 0
    for raw in criteria:
        if not isinstance(raw, dict) or raw.get("kind") not in {"class", "field", "constructor", "method"}:
            raise ValueError("Loại tiêu chí OOP không hợp lệ.")
        criterion = {"kind": raw["kind"]}
        if raw["kind"] in {"field", "method"}:
            criterion["name"] = _identifier(raw.get("name"), "Tên thành phần")
        if raw["kind"] == "field":
            criterion["type"] = _identifier(raw.get("type"), "Kiểu thuộc tính", TYPES)
        if raw["kind"] in {"constructor", "method"}:
            parameters = raw.get("parameters", [])
            if not isinstance(parameters, list) or len(parameters) > 12:
                raise ValueError("Danh sách tham số không hợp lệ.")
            criterion["parameters"] = [_identifier(item, "Kiểu tham số", TYPES) for item in parameters]
            if raw["kind"] == "method":
                criterion["return_type"] = _identifier(raw.get("return_type"), "Kiểu trả về", TYPES)
        access = raw.get("access", "public")
        if access not in ACCESS:
            raise ValueError("Phạm vi truy cập không hợp lệ.")
        criterion["access"] = access
        if raw["kind"] in {"class", "field", "method"}:
            for flag in ("static", "final"):
                if flag in raw:
                    if raw["kind"] == 'class' and flag == 'static':
                        raise ValueError('Lớp Java cấp cao nhất không có modifier static.')
                    if not isinstance(raw[flag], bool):
                        raise ValueError(f"Giá trị {flag} phải là đúng hoặc sai.")
                    criterion[flag] = raw[flag]
        if raw["kind"] == "class":
            parent = raw.get("extends", "")
            interfaces = raw.get("implements", [])
            if parent:
                _identifier(parent, "Lớp cha", QUALIFIED)
            if not isinstance(interfaces, list) or len(interfaces) > 12:
                raise ValueError("Danh sách interface không hợp lệ.")
            criterion.update(extends=parent, implements=[_identifier(item, "Interface", QUALIFIED) for item in interfaces])
        try:
            weight = float(raw.get("points", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Điểm tiêu chí OOP không hợp lệ.") from exc
        if not 0 < weight <= points or round(weight, 2) != weight:
            raise ValueError("Điểm tiêu chí OOP phải dương và tối đa 2 chữ số thập phân.")
        criterion["points"] = weight
        criterion["label"] = str(raw.get("label") or _label(criterion))[:120]
        cleaned.append(criterion)
        total += weight
    if round(total, 2) > points:
        raise ValueError("Tổng điểm tiêu chí OOP vượt điểm bài toán.")
    return {"version": 1, "class_name": name, "package": package, "criteria": cleaned}


def _label(item):
    if item["kind"] == "class":
        return "Lớp và package"
    if item["kind"] == "constructor":
        return "Constructor(" + ", ".join(item["parameters"]) + ")"
    return {"field": "Thuộc tính ", "method": "Phương thức "}[item["kind"]] + item["name"]


def tests(rubric):
    if not rubric:
        return []
    return [{"input": "", "output": "true", "sample": False,
             "feedback_visibility": "hide", "criterion": item["label"], "category": "structure", "points": item["points"],
             "test_code": _code(rubric, item)} for item in rubric["criteria"]]


def _code(rubric, item):
    """Reflection uses string type names, so a missing member fails one criterion, not compilation."""
    target = (rubric["package"] + "." if rubric["package"] else "") + rubric["class_name"]
    quoted = lambda value: json.dumps(value, ensure_ascii=True)
    prelude = f'boolean ok=false; try {{ Class<?> cls=Class.forName({quoted(target)}, false, Thread.currentThread().getContextClassLoader()); '
    access = item["access"]
    modifiers = f'java.lang.reflect.Modifier.toString(member.getModifiers()).contains({quoted(access)})' if access != "package" else '!(java.lang.reflect.Modifier.isPublic(member.getModifiers()) || java.lang.reflect.Modifier.isProtected(member.getModifiers()) || java.lang.reflect.Modifier.isPrivate(member.getModifiers()))'
    if access != "package":
        modifiers = f'java.lang.reflect.Modifier.is{access.title()}(member.getModifiers())'
    if item["kind"] == "class":
        body = 'ok=' + modifiers.replace('member.getModifiers()', 'cls.getModifiers()')
        if item.get("final") is not None:
            body += f' && java.lang.reflect.Modifier.isFinal(cls.getModifiers())=={str(item["final"]).lower()}'
        if item.get("extends"):
            body += f' && cls.getSuperclass()!=null && cls.getSuperclass().getName().equals({quoted(item["extends"])})'
        for interface in item.get("implements", []):
            body += f' && java.util.Arrays.stream(cls.getInterfaces()).anyMatch(x -> x.getName().equals({quoted(interface)}))'
        body += ';'
    elif item["kind"] == "field":
        body = f'java.lang.reflect.Field member=cls.getDeclaredField({quoted(item["name"])}); ok=member.getType().getCanonicalName().equals({quoted(item["type"])}) && {modifiers};'
    else:
        selector = 'getDeclaredConstructors()' if item["kind"] == "constructor" else 'getDeclaredMethods()'
        typ = 'Constructor<?>' if item["kind"] == "constructor" else 'Method'
        body = f'for(java.lang.reflect.{typ} member:cls.{selector}) {{ Class<?>[] parameterTypes=member.getParameterTypes(); if(parameterTypes.length!={len(item["parameters"])}) continue; boolean match=true;'
        for index, parameter in enumerate(item["parameters"]):
            body += f'match &= parameterTypes[{index}].getCanonicalName().equals({quoted(parameter)});'
        if item["kind"] == "method":
            body += f'match &= member.getName().equals({quoted(item["name"])}); match &= member.getReturnType().getCanonicalName().equals({quoted(item["return_type"])});'
        body += f'if(match && {modifiers}) {{ ok=true; break; }} }}'
    if item["kind"] in {"field", "method"}:
        for flag in ("static", "final"):
            if flag in item:
                body = body.replace('ok=', f'ok=java.lang.reflect.Modifier.is{flag.title()}(member.getModifiers())=={str(item[flag]).lower()} && ', 1) if item["kind"] == "field" else body.replace('if(match && ', f'if(match && java.lang.reflect.Modifier.is{flag.title()}(member.getModifiers())=={str(item[flag]).lower()} && ', 1)
    return prelude + body + ' } catch (ReflectiveOperationException ignored) { ok=false; } System.out.print(ok);'
