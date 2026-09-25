from app.rag.vector_store import get_vector_store
from app.llm.llm_chat import ChatLLM
from app.config.settings import RECALL_TOP_K, ENABLE_RERANK

RECALL_MULTIPLIER = 3

def get_chain(user_query: str) -> str:
    llm = ChatLLM.get_instance()
    vector_store = get_vector_store()

    if ENABLE_RERANK:
        recall_k = RECALL_TOP_K * RECALL_MULTIPLIER
        retriever = vector_store.as_retriever(search_kwargs={"k": recall_k})
        docs = retriever.invoke(user_query)
        if not docs:
            return "【知识库未查询到相关内容】"
        from app.rag.rerank import rerank_documents
        docs = rerank_documents(user_query, docs, top_k=RECALL_TOP_K)
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": RECALL_TOP_K})
        docs = retriever.invoke(user_query)
        if not docs:
            return "【知识库未查询到相关内容】"

    context = "\n\n".join(doc.page_content for doc in docs)
    print(f"[RAG] 检索到 {len(docs)} 条文档:")
    for i, doc in enumerate(docs):
        score = doc.metadata.get("rerank_score", "N/A")
        source = doc.metadata.get("source", "未知")
        print(f"  [{i+1}] 分数={score} | 来源={source}")

    sys_prompt = f"""
    你是企业内部知识库助手，请严格依据下面提供的上下文回答用户问题。
    如果上下文中没有相关信息，直接回答：【知识库未查询到相关内容】，不要编造信息，不要幻觉。
    上下文：
    {context}
    """
    answer = llm.chat_with_sys_prompt(user_query, sys_prompt)
    return answer