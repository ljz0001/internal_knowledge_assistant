from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ApiResponse,
    RagDeleteRequest,
    RagFileResponse,
    RagFilesResponse,
    RagSearchRequest,
)
from app.rag.rag_server import (
    rag_add_file,
    rag_add_files,
    rag_delete_file,
    rag_search,
)
from app.rag.vector_store import get_vector_store

router = APIRouter(prefix="/rag", tags=["知识库"])


@router.post("/search", response_model=ApiResponse, summary="检索知识库")
def search(request: RagSearchRequest):
    try:
        return ApiResponse(data={"answer": rag_search(request.query)})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"知识库检索失败：{exc}") from exc


@router.post("/files", response_model=ApiResponse, summary="添加知识库文件")
def add_file(request: RagFileResponse):
    try:
        rag_add_file(request.file_path)
        return ApiResponse(data={"file_path": request.file_path})
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文件入库失败：{exc}") from exc


@router.post("/files/batch", response_model=ApiResponse, summary="批量添加知识库文件")
def add_files(request: RagFilesResponse):
    if not request.file_paths:
        raise HTTPException(status_code=400, detail="file_paths不能为空")
    return ApiResponse(data=rag_add_files(request.file_paths))


@router.delete("/files", response_model=ApiResponse, summary="删除知识库文件")
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
