from langchain_openai import ChatOpenAI
from app.rag.vector_store import get_retriever

from app.llm.llm_chat import ChatLLM

def get_chain(user_query:str) -> str:
    
    retriever = get_retriever()

    llm = ChatLLM.get_instance()

    resp = retriever.invoke(user_query)

    context = "\n\n".join(doc.page_content for doc in resp)

    sys_prompt = f"""
    你是企业内部知识库助手，请严格依据下面提供的上下文回答用户问题。
    如果上下文中没有相关信息，直接回答：【知识库未查询到相关内容】，不要编造信息，不要幻觉。
    上下文：
    {context}
    """
    answer = llm.chat_with_sys_prompt(user_query,sys_prompt)

    return answer