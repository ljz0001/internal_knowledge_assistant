from langchain.tools import tool
from app.common.logger import logger
from app.tools.result import error, invalid_input, not_found, success, unsupported
from app.rag.rag_server import (
    rag_search,
    rag_add_file,
    rag_add_files,
    rag_delete_file
)
from app.rag.vector_store import get_vector_store

@tool
def rag_search_tool(query: str) -> dict:
    """从企业知识库中检索相关信息并回答用户问题。当用户询问公司制度、流程、规定等知识类问题时使用此工具。"""
    if not query or not query.strip():
        return invalid_input("请提供要检索的问题", "RAG_QUERY_EMPTY")
    try:
        answer = rag_search(query.strip())
        if not answer:
            return not_found("知识库中没有找到相关内容")
        return success(answer)
    except Exception:
        logger.exception("知识库检索工具执行失败")
        return error("知识库检索服务暂时不可用，请稍后重试", "RAG_SEARCH_ERROR")

@tool
def rag_add_file_tool(file_path: str) -> dict:
    """将本地文件（txt/md/pdf）上传到知识库中，使其可被检索到。参数file_path是文件的完整路径。"""
    if not file_path or not file_path.strip():
        return invalid_input("请提供要入库的文件路径", "RAG_FILE_PATH_EMPTY")
    try:
        rag_add_file(file_path)
        return success({"file_path": file_path}, f"文件 {file_path} 已成功入库")
    except FileNotFoundError:
        return not_found(f"未找到文件：{file_path}")
    except ValueError as exc:
        return unsupported(str(exc), "RAG_FILE_NOT_SUPPORTED")
    except Exception:
        logger.exception("知识库单文件入库工具执行失败")
        return error("知识库入库服务暂时不可用，请稍后重试", "RAG_ADD_FILE_ERROR")

@tool
def rag_add_files_tool(file_paths: list[str]) -> dict:
    """将本地文件（txt/md/pdf）批量上传到知识库中，使其可被检索到。参数file_paths是文件路径列表，每个路径是一个文件的完整路径。"""
    if not file_paths:
        return invalid_input("请至少提供一个文件路径", "RAG_FILE_PATHS_EMPTY")
    try:
        rag_add_files(file_paths)
        return success({"file_paths": file_paths}, f"已添加 {len(file_paths)} 个文件")
    except FileNotFoundError as exc:
        return not_found(str(exc))
    except ValueError as exc:
        return unsupported(str(exc), "RAG_FILES_NOT_SUPPORTED")
    except Exception:
        logger.exception("知识库批量入库工具执行失败")
        return error("知识库批量入库服务暂时不可用，请稍后重试", "RAG_ADD_FILES_ERROR")

@tool
def rag_delete_file_tool(file_path: str) -> dict:
    """从知识库中删除指定文件的所有向量数据。参数file_path是要删除文件的完整路径。"""
    if not file_path or not file_path.strip():
        return invalid_input("请提供要删除的文件路径", "RAG_FILE_PATH_EMPTY")
    try:
        rag_delete_file(file_path)
        return success({"file_path": file_path}, f"文件 {file_path} 的向量已删除")
    except FileNotFoundError:
        return not_found(f"未找到文件：{file_path}")
    except Exception:
        logger.exception("知识库删除工具执行失败")
        return error("知识库删除服务暂时不可用，请稍后重试", "RAG_DELETE_FILE_ERROR")


@tool
def rag_stats_tool() -> dict:
    """查看知识库向量库的统计信息，包括向量总数和已入库的文件列表。"""
    try:
        vs = get_vector_store()
        total = vs._collection.count()
        sources = set()
        if total > 0:
            all_data = vs._collection.get(limit=10000)
            for meta in all_data["metadatas"]:
                if meta and "source" in meta:
                    sources.add(meta["source"])
        return success({"vector_count": total, "files": sorted(sources)}, f"向量库共有 {total} 条向量，涉及 {len(sources)} 个文件")
    except Exception:
        logger.exception("知识库统计工具执行失败")
        return error("知识库统计服务暂时不可用，请稍后重试", "RAG_STATS_ERROR")
