from langchain.tools import tool
from app.db.session import SessionLocal
from app.db.crud.att_crud import (
    get_attendance_by_date,
    get_attendance_by_emp_id,
    #add_attendance,
    #update_attendance
)
from app.db.crud.contact_crud import (
    get_contact_by_name,
    get_contact_by_id,
    #add_contact,
    #update_contact,
    #delete_contact
)
from app.db.crud.emp_crud import (
    get_employee_by_id,
    get_employee_by_no,
    get_employee_list,
    #add_employee,
    #update_employee,
    #delete_employee
)
from app.db.crud.leave_crud import (
    get_leave_by_id,
    get_leave_by_start_date,
    #add_leave,
    #update_leave
)

@tool
def query_employee_tool(emp_no: str = "", emp_name: str = "") -> str:
    """查询员工信息。可通过工号(emp_no)精确查找，或通过姓名(emp_name)模糊查找。"""
    db = SessionLocal()
    try:
        if emp_no:
            emp = get_employee_by_no(db, emp_no)
            if emp:
                return f"员工信息：\n  姓名：{emp.emp_name}\n  工号：{emp.emp_no}\n  部门：{emp.department}\n  手机：{emp.phone or '无'}"
            return f"未找到工号为 {emp_no} 的员工"
        elif emp_name:
            emps = get_employee_list(db)
            matches = [e for e in emps if emp_name in (e.emp_name or "")]
            if matches:
                parts = []
                for e in matches:
                    parts.append(f"  姓名：{e.emp_name}，工号：{e.emp_no}，部门：{e.department}，手机：{e.phone or '无'}")
                return f"找到 {len(matches)} 个员工：\n" + "\n".join(parts)
            return f"未找到姓名包含 '{emp_name}' 的员工"
        else:
            return "请提供工号(emp_no)或姓名(emp_name)"
    finally:
        db.close()


# @tool
# def add_employee_tool(emp_name: str, emp_no: str, department: str, phone: str = "") -> str:
#     """新增员工。必填：姓名(emp_name)、工号(emp_no)、部门(department)；选填：手机(phone)。"""
#     db = SessionLocal()
#     try:
#         emp_info = {"emp_name": emp_name, "emp_no": emp_no, "department": department}
#         if phone:
#             emp_info["phone"] = phone
#         emp = add_employee(db, emp_info)
#         return f"员工新增成功：ID={emp.id}，姓名={emp.emp_name}，工号={emp.emp_no}"
#     finally:
#         db.close()


@tool
def query_attendance_tool(emp_id: int = 0, date: str = "") -> str:
    """查询考勤记录。可通过员工ID(emp_id)查询某员工全部考勤，或通过日期(date, 格式YYYY-MM-DD)查询某天所有考勤。"""
    db = SessionLocal()
    try:
        records = []
        if emp_id:
            records = get_attendance_by_date(db, date) if date else []
            if not records:
                from app.db.crud.att_crud import get_attendance_by_emp_id
                records = get_attendance_by_emp_id(db, emp_id)
        elif date:
            records = get_attendance_by_date(db, date)
        else:
            return "请提供员工ID(emp_id)或日期(date)"
        
        if not records:
            return "未找到考勤记录"
        parts = []
        for r in records:
            parts.append(f"  日期：{r.attend_date}，上班：{r.check_in}，下班：{r.check_out}，状态：{r.status}")
        return f"共 {len(records)} 条考勤记录：\n" + "\n".join(parts)
    finally:
        db.close()


# @tool
# def add_attendance_tool(emp_id: int, attend_date: str, check_in: str, check_out: str, status: str = "正常") -> str:
#     """新增考勤记录。参数：员工ID(emp_id)、日期(attend_date, YYYY-MM-DD)、上班打卡(check_in, HH:MM:SS)、下班打卡(check_out, HH:MM:SS)、状态(status, 默认正常)。"""
#     db = SessionLocal()
#     try:
#         info = {"emp_id": emp_id, "attend_date": attend_date, "check_in": check_in, "check_out": check_out, "status": status}
#         rec = add_attendance(db, info)
#         return f"考勤记录新增成功：ID={rec.id}，员工ID={rec.emp_id}，日期={rec.attend_date}"
#     finally:
#         db.close()

@tool
def query_leave_tool(emp_id: int = 0, start_date: str = "") -> str:
    """查询请假记录。可通过员工ID(emp_id)查询全部请假，或通过开始日期(start_date, YYYY-MM-DD)查询某天开始的请假。"""
    db = SessionLocal()
    try:
        records = []
        if emp_id:
            records = get_leave_by_id(db, emp_id)
        elif start_date:
            records = get_leave_by_start_date(db, start_date)
        else:
            return "请提供员工ID(emp_id)或开始日期(start_date)"
        
        if not records:
            return "未找到请假记录"
        parts = []
        for r in records:
            parts.append(f"  ID：{r.id}，员工ID：{r.emp_id}，类型：{r.leave_type}，时间：{r.start_date} 至 {r.end_date}，原因：{r.reason}，状态：{r.audit_status}")
        return f"共 {len(records)} 条请假记录：\n" + "\n".join(parts)
    finally:
        db.close()

# @tool
# def add_leave_tool(emp_id: int, leave_type: str, start_date: str, end_date: str, reason: str) -> str:
#     """新增请假申请。参数：员工ID(emp_id)、请假类型(leave_type)、开始日期(start_date, YYYY-MM-DD)、结束日期(end_date, YYYY-MM-DD)、原因(reason)。"""
#     db = SessionLocal()
#     try:
#         info = {"emp_id": emp_id, "leave_type": leave_type, "start_date": start_date, "end_date": end_date, "reason": reason}
#         rec = add_leave(db, info)
#         return f"请假申请新增成功：ID={rec.id}，员工ID={rec.emp_id}，类型={rec.leave_type}"
#     finally:
#         db.close()

@tool
def query_contact_tool(name: str = "", contact_id: int = 0) -> str:
    """查询通讯录联系人。可通过姓名(name)模糊搜索或ID(contact_id)精确查询。"""
    db = SessionLocal()
    try:
        if name:
            contacts = get_contact_by_name(db, name)
            if not contacts:
                return f"未找到姓名包含 '{name}' 的联系人"
            parts = []
            for c in contacts:
                parts.append(f"  姓名：{c.name}，手机：{c.phone}，部门：{c.department}，备注：{c.remark or '无'}")
            return f"找到 {len(contacts)} 个联系人：\n" + "\n".join(parts)
        elif contact_id:
            c = get_contact_by_id(db, contact_id)
            if c:
                return f"联系人信息：\n  姓名：{c.name}\n  手机：{c.phone}\n  部门：{c.department}\n  备注：{c.remark or '无'}"
            return f"未找到ID为 {contact_id} 的联系人"
        else:
            return "请提供姓名(name)或ID(contact_id)"
    finally:
        db.close()

# @tool
# def add_contact_tool(name: str, phone: str, department: str, remark: str = "") -> str:
#     """新增联系人。必填：姓名(name)、手机(phone)、部门(department)；选填：备注(remark)。"""
#     db = SessionLocal()
#     try:
#         info = {"name": name, "phone": phone, "department": department}
#         if remark:
#             info["remark"] = remark
#         c = add_contact(db, info)
#         return f"联系人新增成功：ID={c.id}，姓名={c.name}，手机={c.phone}"
#     finally:
#         db.close()

# @tool
# def update_employee_tool(emp_id: int, emp_name: str = "", emp_no: str = "", department: str = "", phone: str = "") -> str:
#     """更新员工信息。必填：员工ID(emp_id)；选填要修改的字段：姓名(emp_name)、工号(emp_no)、部门(department)、手机(phone)。只传需要修改的字段。"""
#     db = SessionLocal()
#     try:
#         update_data = {}
#         if emp_name:
#             update_data["emp_name"] = emp_name
#         if emp_no:
#             update_data["emp_no"] = emp_no
#         if department:
#             update_data["department"] = department
#         if phone:
#             update_data["phone"] = phone
#         if not update_data:
#             return "请至少提供一个要修改的字段"
#         emp = update_employee(db, emp_id, update_data)
#         if emp:
#             return f"员工信息更新成功：ID={emp.id}，姓名={emp.emp_name}，部门={emp.department}"
#         return f"未找到ID为 {emp_id} 的员工"
#     finally:
#         db.close()

# @tool
# def delete_employee_tool(emp_id: int) -> str:
#     """删除员工。必填：员工ID(emp_id)。"""
#     db = SessionLocal()
#     try:
#         result = delete_employee(db, emp_id)
#         if result:
#             return f"员工ID={emp_id} 已删除"
#         return f"未找到ID为 {emp_id} 的员工"
#     finally:
#         db.close()

# @tool
# def update_attendance_tool(emp_id: int, check_in: str = "", check_out: str = "", status: str = "") -> str:
#     """更新员工考勤记录。必填：员工ID(emp_id)；选填要修改的字段：上班打卡(check_in, HH:MM:SS)、下班打卡(check_out, HH:MM:SS)、状态(status)。"""
#     db = SessionLocal()
#     try:
#         update_data = {}
#         if check_in:
#             update_data["check_in"] = check_in
#         if check_out:
#             update_data["check_out"] = check_out
#         if status:
#             update_data["status"] = status
#         if not update_data:
#             return "请至少提供一个要修改的字段"
#         rec = update_attendance(db, emp_id, update_data)
#         if rec:
#             return f"考勤更新成功：员工ID={emp_id}，日期={rec.attend_date}，状态={rec.status}"
#         return f"未找到员工ID={emp_id} 的考勤记录"
#     finally:
#         db.close()

# @tool
# def update_leave_tool(emp_id: int, leave_type: str = "", start_date: str = "", end_date: str = "", reason: str = "", audit_status: str = "") -> str:
#     """更新请假申请。必填：员工ID(emp_id)；选填要修改的字段：请假类型(leave_type)、开始日期(start_date)、结束日期(end_date)、原因(reason)、审核状态(audit_status)。"""
#     db = SessionLocal()
#     try:
#         update_data = {}
#         if leave_type:
#             update_data["leave_type"] = leave_type
#         if start_date:
#             update_data["start_date"] = start_date
#         if end_date:
#             update_data["end_date"] = end_date
#         if reason:
#             update_data["reason"] = reason
#         if audit_status:
#             update_data["audit_status"] = audit_status
#         if not update_data:
#             return "请至少提供一个要修改的字段"
#         rec = update_leave(db, emp_id, update_data)
#         if rec:
#             return f"请假申请更新成功：ID={rec.id}，员工ID={rec.emp_id}，状态={rec.audit_status}"
#         return f"未找到员工ID={emp_id} 的请假记录"
#     finally:
#         db.close()

# @tool
# def update_contact_tool(contact_id: int, name: str = "", phone: str = "", department: str = "", remark: str = "") -> str:
#     """更新联系人信息。必填：联系人ID(contact_id)；选填要修改的字段：姓名(name)、手机(phone)、部门(department)、备注(remark)。"""
#     db = SessionLocal()
#     try:
#         update_data = {}
#         if name:
#             update_data["name"] = name
#         if phone:
#             update_data["phone"] = phone
#         if department:
#             update_data["department"] = department
#         if remark:
#             update_data["remark"] = remark
#         if not update_data:
#             return "请至少提供一个要修改的字段"
#         c = update_contact(db, contact_id, update_data)
#         if c:
#             return f"联系人更新成功：ID={c.id}，姓名={c.name}，手机={c.phone}"
#         return f"未找到ID为 {contact_id} 的联系人"
#     finally:
#         db.close()

# @tool
# def delete_contact_tool(contact_id: int) -> str:
#     """删除联系人。必填：联系人ID(contact_id)。"""
#     db = SessionLocal()
#     try:
#         result = delete_contact(db, contact_id)
#         if result:
#             return f"联系人ID={contact_id} 已删除"
#         return f"未找到ID为 {contact_id} 的联系人"
#     finally:
#         db.close()

@tool
def get_employee_by_id_tool(emp_id: int) -> str:
    """通过员工ID精确查询员工信息。"""
    db = SessionLocal()
    try:
        emp = get_employee_by_id(db, emp_id)
        if emp:
            return f"员工信息：\n  ID：{emp.id}\n  姓名：{emp.emp_name}\n  工号：{emp.emp_no}\n  部门：{emp.department}\n  手机：{emp.phone or '无'}"
        return f"未找到ID为 {emp_id} 的员工"
    finally:
        db.close()

@tool
def get_leave_by_start_date_tool(start_date: str) -> str:
    """通过开始日期查询请假记录。参数start_date格式为YYYY-MM-DD。"""
    db = SessionLocal()
    try:
        records = get_leave_by_start_date(db, start_date)
        if not records:
            return f"未找到 {start_date} 开始的请假记录"
        parts = []
        for r in records:
            parts.append(f"  ID：{r.id}，员工ID：{r.emp_id}，类型：{r.leave_type}，时间：{r.start_date} 至 {r.end_date}，原因：{r.reason}")
        return f"共 {len(records)} 条记录：\n" + "\n".join(parts)
    finally:
        db.close()