
#==============================通讯录表==============================
from sqlalchemy import Column,Integer,String,Text
from app.db.session import Base
from app.db.models import BaseModelMixin

class Contact(Base,BaseModelMixin):
    __tablename__ = "t_contact"

    id = Column(
            Integer,
            primary_key = True,
            autoincrement = True,
            comment = "通讯录id"
        )
    name = Column(
        String(50),
        nullable = False,
        comment = "联系人姓名"
    )
    phone = Column(
        String(50),
        nullable = False,
        comment = "联系人手机号"
    )
    department = Column(
        String(50),
        nullable = False,
        comment = "联系人所属部门"
    )
    remark = Column(
        Text,
        nullable=True,
        comment="备注：外部合作/实习生"
    )
