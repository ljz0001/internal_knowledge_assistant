from langchain.tools import tool
from app.rag.rag_server import (
    rag_search,
    rag_add_file,
    rag_add_files,
    rag_delete_file
)
from app.rag.vector_store import get_vector_store

@tool
def rag_search_tool(query: str) -> str:
    """从企业知识库中检索相关信息并回答用户问题。当用户询问公司制度、流程、规定等知识类问题时使用此工具。"""
    return rag_search(query)

@tool
def rag_add_file_tool(file_path: str) -> str:
    """将本地文件（txt/md/pdf）上传到知识库中，使其可被检索到。参数file_path是文件的完整路径。"""
    try:
        rag_add_file(file_path)
        return f"文件 {file_path} 已成功入库"
    except Exception as e:
        return f"入库失败：{str(e)}"

@tool
def rag_add_files_tool(file_paths:list[str]) -> str:
    """将本地文件（txt/md/pdf）批量上传到知识库中，使其可被检索到。参数file_paths是文件路径列表，每个路径是一个文件的完整路径。"""
    try:
        rag_add_files(file_paths)
        return f"已添加文件：{file_paths}"
    except Exception as e:
        return f"添加失败：{str(e)}"

@tool
def rag_delete_file_tool(file_path: str) -> str:
    """从知识库中删除指定文件的所有向量数据。参数file_path是要删除文件的完整路径。"""
    try:
        rag_delete_file(file_path)
        return f"文件 {file_path} 的向量已删除"
    except Exception as e:
        return f"删除失败：{str(e)}"


@tool
def rag_stats_tool() -> str:
    """查看知识库向量库的统计信息，包括向量总数和已入库的文件列表。"""
    vs = get_vector_store()
    total = vs._collection.count()
    result = f"向量库统计：共 {total} 条向量"
    if total > 0:
        all_data = vs._collection.get(limit=10000)
        sources = set()
        for meta in all_data["metadatas"]:
            if meta and "source" in meta:
                sources.add(meta["source"])
        result += f"\n涉及 {len(sources)} 个文件："
        for s in sorted(sources):
            result += f"\n  - {s}"
    return result