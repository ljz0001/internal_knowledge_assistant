# 把4个业务路由文件（chat/rag/agent/db）的路由装到一起
from fastapi import APIRouter

# 导入4个业务路由（每个业务文件里都有一个router对象）
from app.api.routers.chat import router as chat_router
from app.api.routers.rag import router as rag_router
from app.api.routers.agent import router as agent_router
from app.api.routers.db import router as db_router

# 创建总路由器
api_router = APIRouter()

# 把每个业务路由挂到总路由上
api_router.include_router(chat_router)   # 自动注册所有/chat/*接口
api_router.include_router(rag_router)    # 自动注册所有/rag/*接口
api_router.include_router(agent_router)  # 自动注册所有/agent/*接口
api_router.include_router(db_router)     # 自动注册所有/db/*接口