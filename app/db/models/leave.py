
#==============================休假申请表==============================

from sqlalchemy import Column,Integer,String,Date,Text
from app.db.session import Base
from app.db.models import BaseModelMixin

class Leave(Base,BaseModelMixin):
    __tablename__ = "t_leave"

    id = Column(
        Integer,
        primary_key = True,
        autoincrement = True,
        comment = "休假申请主键"
    )
    emp_id = Column(
        Integer,
        nullable = False,
        comment = "员工ID,关联t_employee表的id字段"
    )
    leave_type = Column(
        String(50),
        nullable = False,
        comment = "请假类型"
    )
    start_date = Column(
        Date,
        nullable = False,
        comment = "请假开始日期"
    )
    end_date = Column(
        Date,
        nullable = False,
        comment = "请假结束日期"
    )
    reason = Column(
        Text,
        nullable = False,
        comment = "请假原因"
    )
    audit_status = Column(
        String(50),
        nullable = False,
        default = "待审核",
        comment= "待审核/通过/驳回"
    )

# End of Leave model.

