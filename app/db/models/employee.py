
#==============================员工数据表==============================

# 导入字段类型工具
from sqlalchemy import Column, Integer, String
# 导入全局数据表父类（来自你已经写完的session.py）
from app.db.session import Base
# 导入时间公共字段类
from app.db.models import BaseModelMixin

# 员工数据表映射类：一个类 = MySQL里一张数据表
class Employee(Base,BaseModelMixin):
    # 固定语法：__tablename__ 声明数据库中真实表名，必须填写
    __tablename__ = "t_employee"

    # 主键自增ID
    id = Column(
        Integer,
        primary_key = True,       # 设置为主键，每条数据唯一标识
        autoincrement = True,     # 数字自动递增，新增数据无需手动传入id
        comment = "主键自增ID"     # 注释
    )
    # 员工姓名
    emp_name = Column(
        String(50),               # 字符串类型，最大存储50个字符
        nullable = False,         # nullable=False：此字段不允许为空，必须传入内容
        comment = "员工姓名"
    )
    # 员工工号（企业内部唯一编号）
    emp_no = Column(
        String(50),
        unique=True,              # unique=True：全局值不可重复，重复插入会报错
        nullable = False,
        comment = "员工工号"
    )
    # 所属部门
    department = Column(
        String(50),
        nullable = False,
        comment = "员工所属部门"
    )
    # 联系手机号(允许为空)
    phone = Column(
        String(50),
        comment = "员工联系手机号"
    )