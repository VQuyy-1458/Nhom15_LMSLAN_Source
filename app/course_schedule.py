"""Generate dated lessons from an ISO-week range, with exact duplicate detection."""
from datetime import date, datetime, time, timedelta, timezone
import re
import secrets
from . import learning
from .storage import atomic_transaction, write_json, utc_now, audit

VN=timezone(timedelta(hours=7))


def parse_week(value):
    try:
        match=re.fullmatch(r'(\d{4})-W(\d{2})',value)
        if not match:raise ValueError()
        return date.fromisocalendar(int(match[1]),int(match[2]),1)
    except (ValueError,TypeError):raise learning.LearningError(400,'Tuần phải có dạng YYYY-Www và tồn tại trong lịch ISO.')


def bulk(session,form,ip):
    if session['role']!='admin':raise learning.LearningError(403,'Chỉ giảng viên được tạo lịch.')
    first,last=parse_week(form.get('start_week','')),parse_week(form.get('end_week',''))
    if first>last or (last-first).days>7*51:raise learning.LearningError(400,'Khoảng lịch phải tăng dần và tối đa 52 tuần.')
    weekday=learning.integer(form,'weekday',1,1,7)
    try:
        start=time.fromisoformat(form.get('start_time',''));end=time.fromisoformat(form.get('end_time',''))
        if start.tzinfo or end.tzinfo or end<=start:raise ValueError()
    except (ValueError,TypeError):raise learning.LearningError(400,'Giờ kết thúc phải sau giờ bắt đầu trong cùng ngày.')
    title=learning.text(form,'title');location=learning.text(form,'location',200,False)
    with learning.LOCK,atomic_transaction():
        data=learning.load();course=learning.course_access(data,form.get('course_id'),session,write=True)
        existing={(e['starts_at'],e.get('ends_at')) for e in data['events'] if e['course_id']==course['id'] and e['kind']=='lesson'}
        created=[];skipped=0;group=secrets.token_hex(10);current=first
        while current<=last:
            day=current+timedelta(days=weekday-1)
            begins=datetime.combine(day,start,VN).astimezone(timezone.utc).isoformat()
            ends=datetime.combine(day,end,VN).astimezone(timezone.utc).isoformat()
            if (begins,ends) in existing:skipped+=1
            else:
                row={'id':secrets.token_hex(10),'course_id':course['id'],'kind':'lesson','title':title,
                    'description':learning.text(form,'description',10000,False),'location':location,
                    'starts_at':begins,'ends_at':ends,'created_at':utc_now(),'series_id':group,
                    'week_number':(current-first).days//7+1,'iso_week':f'{day.isocalendar().year}-W{day.isocalendar().week:02}'}
                data['events'].append(row);created.append(row['id']);existing.add((begins,ends))
            current+=timedelta(days=7)
        write_json('learning.json',data)
        audit('learning.bulk_schedule',session['user_id'],ip,{'course_id':course['id'],'created':len(created),'skipped':skipped})
        return {'ok':True,'ids':created,'created':len(created),'skipped':skipped}
