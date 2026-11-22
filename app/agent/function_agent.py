"""Function-calling Agent 的组装和统一工具结果处理。"""

import json

from langchain.agents.factory import create_agent
from langchain_core.messages import HumanMessage
from app.llm.llm_chat import ChatLLM
from app.tools import ALL_TOOLS
from app.memory import get_memory_saver
from app.common.logger import logger

SYSTEM_PROMPT = """你是企业内部智能助手，可以使用以下工具帮助用户：

【知识库工具】
- rag_search_tool：检索公司制度、流程等知识
- rag_add_file_tool / rag_add_files_tool：将文档入库
- rag_delete_file_tool：删除文档
- rag_stats_tool：查看知识库统计

【数据库工具（⚠️ 仅查询，无增删改！）】
- 员工：query_employee_tool（按姓名/工号查）、get_employee_by_id_tool（按ID查）
- 考勤：query_attendance_tool（按员工ID或日期查）
- 请假：query_leave_tool（按员工ID或日期查）、get_leave_by_start_date_tool（按开始日期查）
- 联系人：query_contact_tool（按姓名或ID查）

⚠️ 重要规则：
数据库工具仅支持查询操作，**绝对不能修改/删除/新增**数据库数据！
如果用户请求修改数据库，请告知：「数据库修改需要管理员通过系统管理界面操作，我目前只有查询权限。」

请根据用户的问题选择合适的工具调用。如果需要多个工具配合，请依次调用。
如果用户的问题超出所有工具能力范围，请直接说明当前不支持该功能，不要为了调用工具而猜测或补造参数。
如果工具返回结构化状态，请严格遵守：
- success：根据 data 正常回答；
- not_found：明确告诉用户没有找到相关数据；
- unsupported：说明当前不支持的操作，并说明工具支持的范围；
- invalid_input：告诉用户缺少或格式错误的参数；
- error：只告诉用户相关服务暂时不可用，不要暴露 traceback、模块名或内部异常。
如果工具返回"未找到"相关信息，请如实告知用户，不要编造信息。"""


def _parse_tool_result(content):
    """兼容 LangChain ToolMessage 的 dict、JSON 字符串和旧文本结果。"""
    if isinstance(content, dict) and content.get("status"):
        return content
    if isinstance(content, str):
        try:
            value = json.loads(content)
            if isinstance(value, dict) and value.get("status"):
                return value
        except (TypeError, ValueError):
            return None
    return None


def _status_answer(status_result: dict) -> str | None:
    status = status_result.get("status")
    message = status_result.get("message") or ""
    if status in {"unsupported", "invalid_input", "not_found"}:
        return message or "当前请求无法完成，请换一种问法。"
    if status == "error":
        return message or "相关服务暂时不可用，请稍后重试。"
    return None

_agent = None

def get_function_agent():
    global _agent
    if _agent is None:
        llm = ChatLLM.get_instance()
        _agent = create_agent(
            model=llm.client,
            tools=ALL_TOOLS,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=get_memory_saver(),
        )
    return _agent

def run_function_agent(user_query: str, session_id: str = "default", agent=None) -> dict:
    try:
        agent = agent or get_function_agent()
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": session_id}}
        )
    except Exception:
        logger.exception("Agent执行失败，已转换为安全提示")
        return {
            "steps": [],
            "answer": "智能助手暂时无法处理这个问题，请稍后重试。",
            "handled": False,
            "status": "error",
        }

    steps = []
    final_answer = ""
    terminal_status = None

    if isinstance(result, dict) and "messages" in result:
        messages = result["messages"]
        for msg in messages:
            parsed_tool_result = _parse_tool_result(getattr(msg, "content", None))
            if parsed_tool_result:
                terminal_status = parsed_tool_result
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    args_str = ", ".join(f"{k}={v}" for k, v in tc["args"].items())
                    steps.append(f"  调用工具: {tc['name']}({args_str})")
            if hasattr(msg, "content") and hasattr(msg, "tool_calls"):
                if not msg.tool_calls and msg.content:
                    final_answer = msg.content
            elif hasattr(msg, "content") and msg.content:
                if not hasattr(msg, "tool_calls"):
                    final_answer = msg.content

    status_answer = _status_answer(terminal_status) if terminal_status else None
    return {
        "steps": steps,
        "answer": status_answer or final_answer or "我暂时无法根据现有资料回答这个问题。",
        "handled": True,
        "status": terminal_status.get("status", "success") if terminal_status else "success",
    }
