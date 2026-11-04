
#==============================考勤表==============================

from sqlalchemy import Column,Integer,String,Date,Time
from app.db.session import Base
from app.db.models import BaseModelMixin

class Attendance(Base,BaseModelMixin):
    __tablename__ = "t_attendance"

    id = Column(
        Integer,
        primary_key = True,
        autoincrement = True,
        comment = "考勤记录主键"
    )
    emp_id = Column(
        Integer,
        nullable = False,
        comment = "员工ID,关联t_employee表的id字段"
    )
    attend_date = Column(
        Date,
        nullable = False,
        comment = "考勤日期"
    )
    check_in = Column(
        Time,
        nullable = False,
        comment = "上班打卡时间"
    )
    check_out = Column(
        Time,
        nullable = False,
        comment = "下班打卡时间"
    )
    status = Column(
        String(50),
        nullable = False,
        default = "正常",
        comment = "正常/迟到/早退/旷工"
    )
