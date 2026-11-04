from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import (
    ApiResponse,
    DocumentBatchRequest,
    KnowledgeDocumentResponse,
    RagDeleteRequest,
    RagFileResponse,
    RagFilesResponse,
    RagSearchRequest,
)
from app.db.crud import knowledge_document_crud
from app.db.models.knowledge_document import DocumentStatus
from app.rag import document_manager
from app.rag.rag_server import (
    approve_document,
    rag_add_file,
    rag_add_files,
    rag_delete_file,
    rag_search,
)
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/rag", tags=["知识库"])


def _document_data(document):
    """只向调用者返回文件元数据，不暴露服务器绝对路径。"""
    return KnowledgeDocumentResponse(
        id=document.id,
        original_name=document.original_name,
        stored_name=document.stored_name,
        file_hash=document.file_hash,
        file_size=document.file_size,
        file_type=document.file_type,
        status=document.status,
        error_message=document.error_message,
        approved_at=document.approved_at,
        create_time=document.create_time,
        update_time=document.update_time,
    ).model_dump()


@router.post(
    "/uploads",
    response_model=ApiResponse,
    status_code=201,
    summary="上传待审核文件",
)
async def upload_documents(
    files: list[UploadFile] = File(..., description="选择一个或多个 txt、md、pdf 文件"),
    db: Session = Depends(get_db),
):
    """所有上传文件先进入 uploads/，不会因上传动作直接进入知识库。"""
    uploaded = []
    failed = []
    for upload in files:
        content = await upload.read(document_manager.MAX_UPLOAD_SIZE + 1)
        try:
            safe_name, suffix = document_manager.validate_file(upload.filename or "", content)
            file_hash = document_manager.calculate_file_hash(content)
            duplicate = knowledge_document_crud.get_document_by_hash(
                db,
                file_hash,
                [DocumentStatus.PENDING, DocumentStatus.APPROVED, DocumentStatus.FAILED],
            )
            if duplicate:
                raise ValueError(f"文件内容重复，已有记录 ID={duplicate.id}，状态={duplicate.status}")

            file_path, stored_name, suffix = document_manager.save_to_uploads(safe_name, content)
            try:
                record = knowledge_document_crud.create_document(
                    db,
                    {
                        "original_name": safe_name,
                        "stored_name": stored_name,
                        "upload_path": str(file_path),
                        "file_hash": file_hash,
                        "file_size": len(content),
                        "file_type": suffix,
                        "status": DocumentStatus.PENDING,
                    },
                )
            except Exception:
                document_manager.remove_file(file_path)
                raise
            uploaded.append(_document_data(record))
        except Exception as exc:
            failed.append({"filename": upload.filename or "", "error": str(exc)})
        finally:
            await upload.close()
    return ApiResponse(data={"uploaded": uploaded, "failed": failed})


@router.get("/uploads", response_model=ApiResponse, summary="查看上传文件及审核状态")
def list_uploaded_documents(
    status: str | None = Query(None, description="可选状态：pending、approved、deleted、failed"),
    db: Session = Depends(get_db),
):
    allowed_statuses = {DocumentStatus.PENDING, DocumentStatus.APPROVED, DocumentStatus.DELETED, DocumentStatus.FAILED}
    if status and status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="无效状态，可选 pending、approved、deleted、failed")
    documents = knowledge_document_crud.list_documents(db, status)
    return ApiResponse(data=[_document_data(document) for document in documents])


@router.get("/uploads/{document_id}", response_model=ApiResponse, summary="查看单个上传文件")
def get_uploaded_document(document_id: int, db: Session = Depends(get_db)):
    document = knowledge_document_crud.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="未找到上传文件记录")
    return ApiResponse(data=_document_data(document))


def _delete_pending_document(db: Session, document_id: int):
    document = knowledge_document_crud.get_document_by_id(db, document_id)
    if not document:
        raise LookupError("未找到上传文件记录")
    if document.status not in (DocumentStatus.PENDING, DocumentStatus.FAILED):
        raise ValueError("只能删除待审核或入库失败的文件；已入库文件请使用正式文档管理流程")
    document_manager.remove_file(document.upload_path)
    return knowledge_document_crud.update_document(
        db,
        document_id,
        {"status": DocumentStatus.DELETED, "upload_path": None, "error_message": None},
    )


@router.delete("/uploads/{document_id}", response_model=ApiResponse, summary="删除待审核文件")
def delete_uploaded_document(document_id: int, db: Session = Depends(get_db)):
    try:
        document = _delete_pending_document(db, document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ApiResponse(data={"id": document.id, "status": document.status})


@router.post("/uploads/delete-batch", response_model=ApiResponse, summary="批量删除待审核文件")
def delete_uploaded_documents(request: DocumentBatchRequest, db: Session = Depends(get_db)):
    results = {"deleted": [], "failed": []}
    for document_id in request.document_ids:
        try:
            document = _delete_pending_document(db, document_id)
            results["deleted"].append({"id": document.id, "status": document.status})
        except Exception as exc:
            results["failed"].append({"id": document_id, "error": str(exc)})
    return ApiResponse(data=results)


def _approve_one(db: Session, document_id: int):
    try:
        document, chunk_count = approve_document(db, document_id)
        return {"id": document.id, "status": document.status, "chunks": chunk_count}
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文件入库失败：{exc}") from exc


@router.post("/uploads/{document_id}/approve", response_model=ApiResponse, summary="批准单个文件并写入知识库")
def approve_uploaded_document(document_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=_approve_one(db, document_id))


@router.post("/uploads/approve-batch", response_model=ApiResponse, summary="批量批准文件并写入知识库")
def approve_uploaded_documents(request: DocumentBatchRequest, db: Session = Depends(get_db)):
    results = {"approved": [], "failed": []}
    for document_id in request.document_ids:
        try:
            results["approved"].append(_approve_one(db, document_id))
        except HTTPException as exc:
            results["failed"].append({"id": document_id, "error": exc.detail, "status_code": exc.status_code})
    return ApiResponse(data=results)


@router.post("/search", response_model=ApiResponse, summary="检索知识库")
def search(request: RagSearchRequest):
    try:
        return ApiResponse(data={"answer": rag_search(request.query)})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"知识库检索失败：{exc}") from exc


@router.post("/files", response_model=ApiResponse, summary="旧版内部调试：按服务器路径直接入库（绕过审核）")
def add_file(request: RagFileResponse):
    try:
        rag_add_file(request.file_path)
        return ApiResponse(data={"file_path": request.file_path})
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文件入库失败：{exc}") from exc


@router.post("/files/batch", response_model=ApiResponse, summary="旧版内部调试：按服务器路径批量入库（绕过审核）")
def add_files(request: RagFilesResponse):
    if not request.file_paths:
        raise HTTPException(status_code=400, detail="file_paths不能为空")
    return ApiResponse(data=rag_add_files(request.file_paths))


@router.delete("/files", response_model=ApiResponse, summary="旧版内部调试：按服务器路径删除向量")
def delete_file(request: RagDeleteRequest):
    try:
        rag_delete_file(request.file_path)
        return ApiResponse(data={"file_path": request.file_path, "deleted": True})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"删除知识库文件失败：{exc}") from exc


@router.get("/stats", response_model=ApiResponse, summary="查看知识库统计")
def stats():
    try:
        collection = get_vector_store()._collection
        records = collection.get(limit=10000) if collection.count() else {"metadatas": []}
        sources = sorted({meta["source"] for meta in records["metadatas"] if meta and meta.get("source")})
        return ApiResponse(data={"vector_count": collection.count(), "files": sources})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"读取知识库统计失败：{exc}") from exc
