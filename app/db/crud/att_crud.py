from sqlalchemy.orm import Session
from app.db.models.attendance import Attendance
from datetime import date

# 根据员工ID查询考勤记录
def get_attendance_by_emp_id(db:Session,emp_id:int):
    return db.query(Attendance).filter(Attendance.emp_id == emp_id).all()


# 根据日期查询考勤记录
def get_attendance_by_date(db:Session,date:date):
    # 如果传的是字符串，自动转为date对象
    if isinstance(date, str):
        date = date.fromisoformat(date)
    return db.query(Attendance).filter(Attendance.attend_date == date).all()


# 添加考勤记录
def add_attendance(db:Session,attendance_info:dict):
    new_attendance = Attendance(**attendance_info)
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


# 更新考勤记录
def update_attendance(db:Session,emp_id:int,update_attendance:dict):
    attendance = get_attendance_by_emp_id(db,emp_id)
    if not attendance:
        return None
    for key,value in update_attendance.items():
        if hasattr(attendance,key):
            setattr(attendance,key,value)
    db.commit()
    db.refresh(attendance)
    return attendance
