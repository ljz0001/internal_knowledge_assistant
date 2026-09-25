#定义API的「数据合同」：前端传什么进来、后端返回什么出去，
# Pydantic会自动校验格式，格式不对直接报错（不用手动判断）

from pydantic import BaseModel, Field
from typing import Optional

# ---------- 统一响应格式（所有接口都用这个返回） ----------
class ApiResponse(BaseModel):
    """统一响应包装，前端只需要按这个格式解析所有接口"""
    code: int = Field(default=0, description="状态码：0=成功，非0=失败")
    msg: str = Field(default="success", description="提示信息")
    data: Optional[dict | list | str] = Field(default=None, description="真正的业务数据")

# ---------- 对话请求相关 ----------
class ChatRequest(BaseModel):
    """用户发起请求体"""
    query: str = Field(...,description = "用户问题，必填")
    session_id: str = Field(default="default", description="会话ID，可选")

# ---------- rag知识库相关 ----------
class RagSearchRequest(BaseModel):
    """用户检索问题请求体"""
    query: str = Field(...,description = "用户问题，必填")

class RagFileResponse(BaseModel):
    """单个文件响应体"""
    file_path: str = Field(..., description="单个文件路径，必填")

class RagFilesResponse(BaseModel):
    """多个文件响应体"""
    file_paths: list[str] = Field(..., description="多个文件路径列表，必填")

class RagDeleteRequest(BaseModel):
    file_path: str = Field(..., description="要删除的文件路径（必填）")

# ---------- 数据库业务相关（人工CRUD用） ----------
# 员工相关
class EmployeeCreate(BaseModel):
    emp_name: str = Field(..., description="姓名")
    emp_no: str = Field(..., description="工号")
    department: str = Field(..., description="部门")
    phone: Optional[str] = Field(default="", description="手机号（可选）")

class EmployeeUpdate(BaseModel):
    """更新员工时所有字段都是可选的，只传要改的字段"""
    emp_name: Optional[str] = None
    emp_no: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None


# 考勤相关
class AttendanceCreate(BaseModel):
    emp_id: int = Field(..., description="员工ID")
    attend_date: str = Field(..., description="日期（YYYY-MM-DD）")
    check_in: str = Field(..., description="上班打卡时间（HH:MM:SS）")
    check_out: str = Field(..., description="下班打卡时间（HH:MM:SS）")
    status: str = Field(default="正常", description="状态（默认正常）")

class AttendanceUpdate(BaseModel):
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    status: Optional[str] = None

# 请假相关
class LeaveCreate(BaseModel):
    emp_id: int = Field(..., description="员工ID")
    leave_type: str = Field(..., description="请假类型（病假/事假/年假）")
    start_date: str = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: str = Field(..., description="结束日期（YYYY-MM-DD）")
    reason: str = Field(..., description="请假原因")

class LeaveUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    reason: Optional[str] = None
    audit_status: Optional[str] = None

# 联系人相关
class ContactCreate(BaseModel):
    name: str = Field(..., description="姓名")
    phone: str = Field(..., description="手机号")
    department: str = Field(..., description="部门")
    remark: Optional[str] = Field(default="", description="备注（可选）")

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    remark: Optional[str] = None