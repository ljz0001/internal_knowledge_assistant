# 支持：TXT、Markdown、可复制文本 PDF
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader

def load_single_text(file_path:Path | str) -> list[Document]:
    """
    加载单个文本文件（TXT、Markdown）
    """
    loader = TextLoader(str(file_path),encoding = "utf-8")
    documents = loader.load()
    return documents

def load_single_pdf(file_path: Path | str) -> list[Document]:
    """
    加载单个PDF文件，自动提取每页文本
    """
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    return docs

def load_documents_from_dir(dir_path: Path | str) -> list[Document]:
    """
    批量遍历目录，自动识别 pdf / txt / md
    """
    all_docs = []
    # 转化成Path对象，使用Path的方法
    base_dir = Path(dir_path)
    """
    rglob("*")：递归 glob遍历base_dir下面所有文件，包括子文件夹里面的文件
    *代表匹配全部；
    """
    for file in base_dir.rglob("*"):
        # file.suffix：Path 自带属性，拿到文件后缀，例如test.PDF → 返回.PDF
        suffix = file.suffix.lower()
        docs: list[Document] = []
        if suffix == ".txt" or suffix == ".md":
            docs = load_single_text(file)
        elif suffix == ".pdf":
            docs = load_single_pdf(file)
        else:
            continue
        # 绑定元数据：文件来源路径
        for doc in docs:
            doc.metadata["source"] = str(file)
        """
        extend：把当前文件解析出来的 Document 列表，全部合并到大列表all_docs。
        区分：append(docs)会把列表塞成嵌套列表；extend是把里面元素拿出来追加。
        """
        all_docs.extend(docs)
    return all_docs
    

