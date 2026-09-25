from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config.settings import(
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE
)

class ChatLLM:
    
    _instance = None
    def __init__(self):
        self.api_key=LLM_API_KEY
        self.base_url=LLM_BASE_URL
        self.model=LLM_MODEL_NAME
        self.temperature=LLM_TEMPERATURE

        self.client = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=self.temperature
        )
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    


    def chat(self,user_query:str) -> str:
        resp = self.client.invoke(
            [HumanMessage(content=user_query)]
            )
        return resp.content
    

    def chat_with_sys_prompt(self,user_query:str,sys_prompt:str) -> str:
        resp = self.client.invoke(
            [SystemMessage(content=sys_prompt),
             HumanMessage(content=user_query)]
            )
        # self.client.invoke() 返回的是 LangChain 对象：AIMessage 对象。
        return resp.content
    
        
    

