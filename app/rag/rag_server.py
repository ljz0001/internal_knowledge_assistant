
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.crud import knowledge_document_crud
from app.db.models.knowledge_document import DocumentStatus
from app.rag.loader import (
    load_documents_from_dir,
    load_single_text,
    load_single_pdf
    )
from app.rag.splitter import get_text_splitter
from app.rag.vector_store import (
    add_documents,
    get_vector_store,
    delete_by_document_id,
    delete_by_source
    )
from app.rag.chain_v2 import get_chain
from app.config.settings import (
    DOCS_DIR
    )
from app.rag import document_manager

def _init_vector_store():
    """初始化rag检索向量库"""
    vs = get_vector_store()
    if vs._collection.count() == 0:
        print("向量库为空，开始全量入库...")
        docs = load_documents_from_dir(DOCS_DIR)
        splitter = get_text_splitter()
        split_docs = splitter.split_documents(docs)
        add_documents(split_docs)
        print(f"入库完成，共 {len(split_docs)} 条向量")

def rag_search(user_query:str) -> str:
    _init_vector_store()
    answer = get_chain(user_query)
    return answer

def rag_add_file(file_path: str, metadata: dict | None = None) -> int:
    """增量添加/更新单个文件到向量库。

    旧版路径接口仍会调用本函数；新版审批流程会传入 document_id、hash 等元数据，
    以便未来能够按文档记录精准删除向量。
    """
    delete_by_source(file_path)
    p = Path(file_path)
    suffix = p.suffix.lower()
    if suffix in [".txt",".md"]:
        docs = load_single_text(file_path)
    elif suffix == ".pdf":
        docs = load_single_pdf(file_path)
    else:
        raise ValueError(f"不支持的文件格式：{suffix}")
    for doc in docs:
        doc.metadata["source"] = file_path
        if metadata:
            doc.metadata.update(metadata)
    
    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    add_documents(chunks)
    print(f"入库完成，共 {len(chunks)} 条向量")
    return len(chunks)

def rag_add_files(file_paths:list[str]):
    """批量添加/更新文件到向量库"""
    
    success = []
    failed = []

    for path in file_paths:
        try:
            count = rag_add_file(path)
            success.append({"path":path,"chunks":count})
        except Exception as e:
            failed.append({"path":path,"error":str(e)})

    return {"success":success,"failed":failed}

def rag_delete_file(file_path:str | Path):
    """删除文件从向量库"""
    delete_by_source(file_path)


def rag_delete_document_vectors(document_id: int) -> None:
    """新版审核流程使用：按 document_id 删除某个已审批文件的所有向量。"""
    delete_by_document_id(document_id)


def approve_document(db: Session, document_id: int):
    """审批一个待处理文件，串联磁盘、向量库和状态表。

    出错时清除本次可能写入的切片、尽量把原文放回 uploads/，并保留 failed 状态供用户查看。
    """
    document = knowledge_document_crud.get_document_by_id(db, document_id)
    if not document:
        raise LookupError("未找到上传文件记录")
    if document.status not in (DocumentStatus.PENDING, DocumentStatus.FAILED):
        raise ValueError(f"当前状态 {document.status} 不允许审批")

    upload_path = document.upload_path
    document_path = None
    try:
        if not upload_path or not Path(upload_path).is_file():
            raise FileNotFoundError("待审核文件不在 uploads/ 中，无法审批")

        content = Path(upload_path).read_bytes()
        if document_manager.calculate_file_hash(content) != document.file_hash:
            raise ValueError("文件内容与上传时不一致，请删除后重新上传")

        # 正式原文先移入 docs/，向量元数据中的 source 也使用这个正式路径。
        document_path = document_manager.move_to_docs(upload_path, document.stored_name)
        chunk_count = rag_add_file(
            str(document_path),
            metadata={
                "document_id": document.id,
                "file_hash": document.file_hash,
                "original_name": document.original_name,
            },
        )
        if chunk_count == 0:
            raise ValueError("文件解析后没有可入库的文本内容")

        approved = knowledge_document_crud.update_document(
            db,
            document.id,
            {
                "status": DocumentStatus.APPROVED,
                "upload_path": None,
                "document_path": str(document_path),
                "error_message": None,
                "approved_at": datetime.now(),
            },
        )
        return approved, chunk_count
    except Exception as exc:
        # Compensation: keep the original available for inspection/retry and remove partial vectors.
        try:
            rag_delete_document_vectors(document.id)
        except Exception:
            pass
        if document_path and Path(document_path).is_file():
            try:
                document_manager.move_to_uploads(document_path, document.stored_name)
            except Exception:
                pass
        knowledge_document_crud.update_document(
            db,
            document.id,
            {
                "status": DocumentStatus.FAILED,
                "upload_path": upload_path,
                "document_path": None,
                "error_message": str(exc)[:4000],
                "approved_at": None,
            },
        )
        raise
