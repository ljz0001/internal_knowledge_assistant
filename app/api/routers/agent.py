from fastapi import APIRouter, Depends, HTTPException

from app.agent.function_agent import run_function_agent
from app.api.deps import get_agent, get_agent_mode
from app.api.schemas import ApiResponse, ChatRequest

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=ApiResponse, summary="调用Agent")
def invoke(request: ChatRequest, agent=Depends(get_agent)):
    try:
        return ApiResponse(data=run_function_agent(request.query, request.session_id, agent=agent))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent调用失败：{exc}") from exc


@router.get("/health", response_model=ApiResponse, summary="Agent服务健康检查")
def health(agent=Depends(get_agent)):
    return ApiResponse(data={"status": "ok"})


@router.get("/mode", response_model=ApiResponse, summary="获取Agent运行模式")
def mode(agent_mode: str = Depends(get_agent_mode)):
    return ApiResponse(data={"mode": agent_mode})
