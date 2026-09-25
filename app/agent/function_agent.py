# app/agent/function_agent.py

from langchain.agents.factory import create_agent
from langchain_core.messages import HumanMessage
from app.llm.llm_chat import ChatLLM
from app.tools import ALL_TOOLS
from app.memory import get_memory_saver

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
如果工具返回"未找到"相关信息，请如实告知用户，不要编造信息。"""

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

def run_function_agent(user_query: str, session_id: str = "default") -> dict:
    agent = get_function_agent()
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_query)]},
        config={"configurable": {"thread_id": session_id}}
        )

    steps = []
    final_answer = ""

    if isinstance(result, dict) and "messages" in result:
        messages = result["messages"]
        for msg in messages:
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

    return {"steps": steps, "answer": final_answer}