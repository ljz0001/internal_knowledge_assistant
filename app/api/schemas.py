#定义API的「数据合同」：前端传什么进来、后端返回什么出去，
# Pydantic会自动校验格式，格式不对直接报错（不用手动判断）

from pydantic import BaseModel, Field
from datetime import date, datetime, time
from typing import Any, Literal, Optional

# ---------- 统一响应格式（所有接口都用这个返回） ----------
class ApiResponse(BaseModel):
    """统一响应包装，前端只需要按这个格式解析所有接口"""
    code: int = Field(default=0, description="状态码：0=成功，非0=失败")
    msg: str = Field(default="success", description="提示信息")
    data: Any = Field(default=None, description="真正的业务数据")

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


# ---------- 新版知识库上传与审核相关 ----------
# 文件二进制由 FastAPI 的 UploadFile 接收；下面模型只描述 JSON 响应和批量操作请求。
DocumentStatusValue = Literal["pending", "approved", "deleted", "failed"]


class KnowledgeDocumentResponse(BaseModel):
    """上传文件在列表中展示的元数据，不返回文件内容。"""

    id: int
    original_name: str
    stored_name: str
    file_hash: str
    file_size: int
    file_type: str
    status: DocumentStatusValue
    error_message: Optional[str] = None
    approved_at: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class DocumentBatchRequest(BaseModel):
    """批量删除或批量审批时提交的文件记录 ID 列表。"""

    document_ids: list[int] = Field(..., min_length=1, description="至少提供一个知识库文件ID")

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
    attend_date: date = Field(..., description="日期（YYYY-MM-DD）")
    check_in: time = Field(..., description="上班打卡时间（HH:MM:SS）")
    check_out: time = Field(..., description="下班打卡时间（HH:MM:SS）")
    status: str = Field(default="正常", description="状态（默认正常）")

class AttendanceUpdate(BaseModel):
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    status: Optional[str] = None

# 请假相关
class LeaveCreate(BaseModel):
    emp_id: int = Field(..., description="员工ID")
    leave_type: str = Field(..., description="请假类型（病假/事假/年假）")
    start_date: date = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: date = Field(..., description="结束日期（YYYY-MM-DD）")
    reason: str = Field(..., description="请假原因")

class LeaveUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
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
