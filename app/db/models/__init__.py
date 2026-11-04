# 导入sqlalchemy内置工具
# Column：用来定义数据表每一列字段
# DateTime：时间类型字段
# func：调用MySQL内置函数
from sqlalchemy import Column, DateTime, func


class BaseModelMixin:
    """
    通用数据表混入类【固定复用模板】
    所有业务数据表都会继承这个类，自动携带创建时间、更新时间
    不用每张表重复编写两段时间字段，统一规范、减少冗余代码
    """
    # create_time：数据创建时间，新增数据时自动填充当前数据库时间
    create_time = Column(
        DateTime,
        default=func.now(),  # 默认值：调用数据库now()获取当前时间
        comment="数据创建时间"
    )

    # update_time：数据最后修改时间，新增/修改内容都会自动刷新时间
    update_time = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),  # 数据更新时自动触发赋值
        comment="数据最后更新时间"
    )