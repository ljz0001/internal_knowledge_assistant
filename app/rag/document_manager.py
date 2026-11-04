"""上传文件的磁盘操作工具：校验、保存、移动和删除，不负责数据库或向量化。"""

import hashlib
import re
from pathlib import Path
from uuid import uuid4

from app.config.settings import DOCS_DIR, UPLOADS_DIR

ALLOWED_FILE_TYPES = {".txt", ".md", ".pdf"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


def sanitize_filename(filename: str) -> str:
    """去掉路径和危险字符，防止用户文件名穿越到目标目录之外。"""
    raw_name = Path(filename or "upload").name
    safe_name = re.sub(r'[^\w.\-\u4e00-\u9fff]+', "_", raw_name, flags=re.UNICODE).strip("._")
    return safe_name or "upload"


def validate_file(filename: str, content: bytes) -> tuple[str, str]:
    safe_name = sanitize_filename(filename)
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_FILE_TYPES:
        raise ValueError(f"不支持的文件格式：{suffix or '无扩展名'}，仅支持 txt、md、pdf")
    if not content:
        raise ValueError("上传文件不能为空")
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError(f"文件超过大小限制：最大允许 {MAX_UPLOAD_SIZE // 1024 // 1024}MB")
    return safe_name, suffix


def calculate_file_hash(content: bytes) -> str:
    """SHA-256 是文件内容指纹，用于判断重复文件或文件版本变化。"""
    return hashlib.sha256(content).hexdigest()


def save_to_uploads(original_name: str, content: bytes) -> tuple[Path, str, str]:
    safe_name, suffix = validate_file(original_name, content)
    stored_name = f"{uuid4().hex}_{safe_name}"
    destination = UPLOADS_DIR / stored_name
    destination.write_bytes(content)
    return destination, stored_name, suffix


def move_to_docs(upload_path: str | Path, stored_name: str) -> Path:
    source = Path(upload_path)
    if not source.is_file():
        raise FileNotFoundError(f"待审核文件不存在：{source}")
    destination = DOCS_DIR / stored_name
    if destination.exists():
        raise FileExistsError(f"正式文档目录已存在同名文件：{destination.name}")
    source.replace(destination)
    return destination


def move_to_uploads(document_path: str | Path, stored_name: str) -> Path:
    """向量化失败时，把刚移动的文件放回待审核目录。"""
    source = Path(document_path)
    destination = UPLOADS_DIR / stored_name
    if source.is_file():
        source.replace(destination)
    return destination


def remove_file(file_path: str | Path | None) -> None:
    if file_path and Path(file_path).exists():
        Path(file_path).unlink()
