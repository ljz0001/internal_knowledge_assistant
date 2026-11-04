"""知识库原文文件的状态记录模型。"""

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.models import BaseModelMixin
from app.db.session import Base


class DocumentStatus:
    """文件生命周期状态，使用字符串便于数据库和前端展示。"""

    PENDING = "pending"
    APPROVED = "approved"
    DELETED = "deleted"
    FAILED = "failed"


class KnowledgeDocument(Base, BaseModelMixin):
    __tablename__ = "t_knowledge_document"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="知识库文件主键")
    original_name = Column(String(255), nullable=False, comment="用户上传时看到的原始文件名")
    stored_name = Column(String(255), nullable=False, unique=True, comment="服务器安全保存名")
    upload_path = Column(String(500), nullable=True, comment="待审核文件在 uploads/ 中的路径")
    document_path = Column(String(500), nullable=True, comment="审核通过文件在 docs/ 中的路径")
    file_hash = Column(String(64), nullable=False, index=True, comment="SHA-256 文件内容指纹")
    file_size = Column(Integer, nullable=False, comment="文件大小，单位为字节")
    file_type = Column(String(20), nullable=False, comment="文件扩展名")
    status = Column(String(20), nullable=False, default=DocumentStatus.PENDING, index=True, comment="文件状态")
    error_message = Column(Text, nullable=True, comment="审批或入库失败说明")
    approved_at = Column(DateTime, nullable=True, comment="审批并成功入库的时间")
