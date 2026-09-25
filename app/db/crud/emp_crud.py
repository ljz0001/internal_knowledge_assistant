# Session：数据库会话对象，代表和MySQL建立的连接通道
from sqlalchemy.orm import Session
# 导入员工表ORM模型
from app.db.models.employee import Employee

#--------固定模板：根据主键ID查询单条数据-----------
# 规则：所有crud函数第一个参数永远是 db:Session，会话统一外部传入，不和底层连接绑定
def get_employee_by_id(db:Session,emp_id:int):
    # 1. db.query(Employee)：开启针对员工表的查询
    # 2. filter()：添加查询条件
    # 3. first()：获取匹配到的第一条数据，查不到返回None
    return db.query(Employee).filter(Employee.id == emp_id).first()

#--------业务自定义查询：根据工号查找员工-----------
def get_employee_by_no(db:Session,emp_no:str):
    return db.query(Employee).filter(Employee.emp_no == emp_no).first()

#--------固定模板：分页查询员工列表--------------
# skip：跳过前N条数据（分页偏移量）；limit：一页最多展示多少条
def get_employee_list(db:Session,skip:int=0,limit:int=20):
    return db.query(Employee).offset(skip).limit(limit).all()

#--------固定模板：新增数据（三段式标准流程：add -> commit -> refresh）-----------
def add_employee(db:Session,emp_info:dict):
    # 字典解包，将传入的员工信息转为ORM对象
    emp_obj = Employee(**emp_info)
    # 1. add：把对象放入缓冲区，此时数据还没写入数据库
    db.add(emp_obj)
    # 2. commit：提交事务，数据真正插入MySQL数据库
    db.commit()
    # 3. refresh：从数据库拉取最新数据，回填自动生成的id、创建时间
    db.refresh(emp_obj)
    return emp_obj

#--------根据id更新员工信息--------------------
def update_employee(db:Session,emp_id:int,update_data:dict):
    emp = get_employee_by_id(db,emp_id)
    if not emp:
        return None
    # 循环更新字段
    for key,value in update_data.items():
        # 判断对象 emp 里面有没有名为 key 的属性
        if hasattr(emp,key):
            # setattr = setattribute，给对象动态设置属性值
            # 三个参数：
            # emp：要修改的对象
            # key：属性名字符串
            # value：要赋的新值
            setattr(emp,key,value)
    
    db.commit()
    db.refresh(emp)
    return emp

#--------根据id删除员工信息--------------------
def delete_employee(db:Session,emp_id:int):
    emp = get_employee_by_id(db,emp_id)
    if not emp:
        return None
    db.delete(emp)
    db.commit()
    return True
