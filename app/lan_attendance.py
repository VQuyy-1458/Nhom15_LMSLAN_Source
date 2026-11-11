"""Attendance from recent authenticated LAN sessions, without treating a roster as online."""
import ipaddress
import time
from datetime import datetime, timezone
from . import learning
from .storage import read_json, write_json, utc_now, atomic_transaction, audit

FRESH_SECONDS = 120
NETWORKS = tuple(ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16','127.0.0.0/8','fc00::/7','fe80::/10','::1/128'))


def lan_ip(value):
    try:
        address=ipaddress.ip_address(value)
        if getattr(address,'ipv4_mapped',None):address=address.ipv4_mapped
        return any(address.version==network.version and address in network for network in NETWORKS)
    except ValueError:return False


def online_students(now=None):
    now=now or datetime.now(timezone.utc)
    students=read_json('students.json');result={}
    for session in read_json('sessions.json').values():
        sid=session.get('user_id')
        try:
            age=(now-learning.date_value(session.get('last_seen'))).total_seconds()
            valid=float(session.get('expires_at',0))>now.timestamp()
        except (learning.LearningError,TypeError,ValueError):continue
        if session.get('role')=='student' and sid in students and students[sid].get('active',True) and valid and -30<=age<=FRESH_SECONDS and lan_ip(session.get('ip','')):
            if sid not in result or session['last_seen']>result[sid]['last_seen']:result[sid]=session
    return result


def record(data,row,sid,ip,now):
    course=learning.find(data,'courses',row['course_id'])
    if course['status']=='completed' or course.get('student_ids') is not None and sid not in course['student_ids']:
        return False
    if sid in row['records'] or row.get('closed') or learning.date_value(row['expires_at'])<=now:
        return False
    if row.get('mode','qr')!='lan' or not lan_ip(ip):return False
    elapsed=(now-learning.date_value(row['created_at'])).total_seconds()
    status='late' if elapsed>row.get('grace_minutes',5)*60 else 'present'
    row['records'][sid]={'status':status,'checked_in_at':now.isoformat(),'ip':ip,'source':'lan','manual':False}
    audit('learning.lan_attendance',sid,ip,{'session_id':row['id'],'status':status})
    return True


def opened(data,row,now=None):
    now=now or datetime.now(timezone.utc)
    return sum(record(data,row,sid,session['ip'],now) for sid,session in online_students(now).items())


def sync_student(session,ip):
    if session.get('role')!='student' or not lan_ip(ip):return 0
    sid=session['user_id']
    student=read_json('students.json').get(sid)
    if not student or not student.get('active',True):return 0
    with learning.LOCK,atomic_transaction():
        data=learning.load();now=datetime.now(timezone.utc)
        changed=sum(record(data,row,sid,ip,now) for row in data['attendance'])
        if changed:write_json('learning.json',data)
        return changed
