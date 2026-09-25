
from pathlib import Path

from app.rag.loader import (
    load_documents_from_dir,
    load_single_text,
    load_single_pdf
    )
from app.rag.splitter import get_text_splitter
from app.rag.vector_store import (
    add_documents,
    get_vector_store,
    delete_by_source
    )
from app.rag.chain_v2 import get_chain
from app.config.settings import (
    DOCS_DIR
    )

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

def rag_add_file(file_path:str):
    """增量添加/更新单个文件到向量库"""
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
    
    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    add_documents(chunks)
    print(f"入库完成，共 {len(chunks)} 条向量")

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