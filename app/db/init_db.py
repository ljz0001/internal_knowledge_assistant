# 导入数据库引擎和基础父类
from app.db.session import engine, Base
# 必须导入所有ORM模型，Base才能识别需要创建哪些数据表
from app.db.models.employee import Employee
from app.db.models.contact import Contact
from app.db.models.leave import Leave
from app.db.models.attendance import Attendance
from app.config.settings import MYSQL_DB
print(f"【调试】读取到的数据库名称 = {MYSQL_DB}")


#----------一键自动创建项目内所有数据表----------------
def create_all_tables():
    # 对比代码模型和数据库现有表，不存在的表自动创建
    """

    Base.metadata.create_all(
    bind=engine,
    checkfirst=True,   # 默认True：建表前检查表是否存在，存在就跳过（咱们现在在用的特性）
    tables=[Employee.__table__] # 只单独创建某一张表，而不是全部表
)

    """

    
    Base.metadata.create_all(bind=engine)
    print("✅ 所有数据表创建成功，请到MySQL中查看！")



"""
   
    # 删除所有表，谨慎使用！开发测试偶尔用，
    # 正式环境绝对禁止
    Base.metadata.drop_all(bind=engine)
    print("✅ 所有数据表删除成功，请到MySQL中查看！")

"""

if __name__ == "__main__":
    create_all_tables()
