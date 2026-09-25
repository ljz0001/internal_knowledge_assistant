from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.rag.embedding import get_embedding_model
from app.config.settings import CHROMA_PERSIST_DIR, RECALL_TOP_K

_chroma_instance:Chroma | None = None

def get_vector_store() -> Chroma:
    
    global _chroma_instance

    if _chroma_instance is None:
        _chroma_instance = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=get_embedding_model()
        )
    return _chroma_instance

def add_documents(documents: list[Document]):
    vector_store = get_vector_store()
    vector_store.add_documents(documents)

def delete_by_source(source_file_path: str) -> None:
    """根据metadata里面source字段，删除对应文件全部向量，实现增量更新"""
    vector_store = get_vector_store()
    # limit调大，避免切片数量多拿不全id，导致删除不干净
    ret = vector_store.get(where={"source": source_file_path}, limit=10000)
    ids = ret["ids"]
    if ids:
        vector_store.delete(ids=ids)

def get_retriever():
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_kwargs={"k": RECALL_TOP_K}
        )