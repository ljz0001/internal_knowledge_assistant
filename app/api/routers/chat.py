from fastapi import APIRouter, Depends
from app.api.schemas import ApiResponse, ChatRequest
from app.api.deps import get_agent
from app.agent.function_agent import run_function_agent
from app.common.logger import logger


# 创建路由组：prefix是路径前缀（这个文件里的接口都以/chat开头），tags是Swagger文档里的分组
router = APIRouter(prefix="/chat", tags=["智能对话"])

# ---------- 对话接口 ----------

@router.post("/", summary="Agent多轮对话", response_model=ApiResponse)
async def chat(request:ChatRequest,agent = Depends(get_agent)):
    """
    与Agent进行多轮对话（支持上下文记忆）
    
    - request: 自动解析的ChatRequest对象（包含query和session_id）
    - agent: 自动注入的Agent单例（不用手动初始化模型）
    """
    try:
        logger.info(f"收到对话请求：query={request.query},session_id={request.session_id}")
        # 调用Agent进行对话
        result = run_function_agent(request.query, request.session_id, agent=agent)
        # 用统一格式返回
        return ApiResponse(data=result)
    except Exception as e:
        logger.exception("对话失败")
        return ApiResponse(code = 5000,msg = f"对话服务异常：{str(e)}")
    


    # ---------- 健康检查接口（不用模型，快速测服务是否通） ----------
@router.get("/health", summary="对话服务健康检查")
async def chat_health(agent=Depends(get_agent)):
    """快速检查Agent是否正常初始化，不用传参数"""
    return ApiResponse(data={"status": "ok"})
