from app.db.crud.emp_crud import (
    get_employee_by_id,
    add_employee,
    update_employee,
    delete_employee
)
from app.db.session import SessionLocal
from app.common.exceptions import MysqlDBException


def add_emp_test(db):
    """新增员工"""
    try:
        emp_info = {
            "emp_name": "测试员工1",
            "emp_no": "1001",
            "department": "测试部",
            "phone": "13800000000"
        }
        new_emp = add_employee(db, emp_info)
        print(f"✅ 新增员工成功，员工ID：{new_emp.id}")
        return new_emp.id
    except Exception as e:
        db.rollback()
        raise MysqlDBException(f"新增员工失败：{str(e)}") from e


def query_emp_test(db):
    """查询员工"""
    try:
        eid = int(input("请输入员工ID："))
        emp = get_employee_by_id(db, eid)
        if emp:
            print(f"📄 ID:{emp.id} 姓名:{emp.emp_name} 工号:{emp.emp_no} 部门:{emp.department} 手机号:{emp.phone}")
        else:
            print("⚠️ 未查询到该员工")
    except Exception as e:
        raise MysqlDBException(f"查询员工失败：{str(e)}") from e


def update_emp_test(db):
    """修改员工"""
    try:
        eid = int(input("请输入待修改员工ID："))
        update_data = {"department": "AI研发部", "phone": "13900001111"}
        emp = update_employee(db, eid, update_data)
        if emp:
            print("✅ 员工信息修改成功")
        else:
            print("⚠️ 找不到对应员工，修改无效")
    except Exception as e:
        db.rollback()
        raise MysqlDBException(f"修改员工失败：{str(e)}") from e


def delete_emp_test(db):
    """删除员工"""
    try:
        eid = int(input("请输入待删除员工ID："))
        result = delete_employee(db, eid)
        if result:
            print("✅ 员工删除成功")
        else:
            print("⚠️ 找不到对应员工，删除无效")
    except Exception as e:
        db.rollback()
        raise MysqlDBException(f"删除员工失败：{str(e)}") from e


def show_menu():
    print("\n========== 员工CRUD测试菜单 ==========")
    print("1. 新增员工")
    print("2. 根据ID查询员工")
    print("3. 修改员工信息")
    print("4. 删除员工")
    print("0. 退出测试程序")
    return input("请输入操作序号：")


def test_db_crud():
    db = SessionLocal()
    print("🔌 数据库会话已建立，可循环执行测试")
    try:
        while True:
            opt = show_menu()
            try:
                if opt == "1":
                    add_emp_test(db)
                elif opt == "2":
                    query_emp_test(db)
                elif opt == "3":
                    update_emp_test(db)
                elif opt == "4":
                    delete_emp_test(db)
                elif opt == "0":
                    print("🛑 即将退出测试程序")
                    break
                else:
                    print("❌ 无效选项，请重新输入！")
            except MysqlDBException as err:
                print(f"❌【数据库异常】code={err.code} msg={err.msg}")
    finally:
        db.close()
        print("✅ 数据库连接已正常释放")


if __name__ == "__main__":
    test_db_crud()
    

