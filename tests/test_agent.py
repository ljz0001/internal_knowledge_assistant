from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.agent.function_agent import run_function_agent
from app.api.deps import get_agent
from app.api.main import app
from app.api.routers import agent as agent_router
from app.tools import ALL_TOOLS


@pytest.fixture
def fake_agent():
    """提供一个可控的 Agent，测试时不会请求真实大模型。"""
    agent = Mock()
    agent.invoke.return_value = {
        "messages": [
            SimpleNamespace(
                tool_calls=[{"name": "query_employee_tool", "args": {"emp_no": "E001"}}],
                content="",
            ),
            SimpleNamespace(tool_calls=[], content="查到员工张三。"),
        ]
    }
    return agent


def test_run_function_agent_returns_answer_and_tool_steps(fake_agent):
    result = run_function_agent("查一下工号 E001", "session-1", agent=fake_agent)

    assert result["answer"] == "查到员工张三。"
    assert result["steps"] == ["  调用工具: query_employee_tool(emp_no=E001)"]
    fake_agent.invoke.assert_called_once()
    args, kwargs = fake_agent.invoke.call_args
    assert args[0]["messages"][0].content == "查一下工号 E001"
    assert kwargs["config"]["configurable"]["thread_id"] == "session-1"


def test_run_function_agent_uses_default_agent_when_not_injected(monkeypatch):
    fake_agent = Mock()
    fake_agent.invoke.return_value = {"messages": [SimpleNamespace(content="你好", tool_calls=[])]}
    get_agent = Mock(return_value=fake_agent)
    monkeypatch.setattr("app.agent.function_agent.get_function_agent", get_agent)

    result = run_function_agent("你好")

    assert result == {"steps": [], "answer": "你好"}
    get_agent.assert_called_once_with()


def test_run_function_agent_propagates_invoke_errors(fake_agent):
    fake_agent.invoke.side_effect = RuntimeError("agent unavailable")

    with pytest.raises(RuntimeError, match="agent unavailable"):
        run_function_agent("测试", agent=fake_agent)


def test_agent_database_tools_remain_read_only():
    database_domains = ("employee", "attendance", "leave", "contact")
    database_tools = {
        tool.name for tool in ALL_TOOLS if any(domain in tool.name for domain in database_domains)
    }

    assert database_tools == {
        "query_employee_tool",
        "get_employee_by_id_tool",
        "query_attendance_tool",
        "query_leave_tool",
        "get_leave_by_start_date_tool",
        "query_contact_tool",
    }
    assert not any(name.startswith(("add_", "update_", "delete_")) for name in database_tools)


def test_agent_invoke_route_uses_injected_agent(client, monkeypatch):
    fake_agent = object()
    run_agent = Mock(return_value={"steps": [], "answer": "已完成"})
    monkeypatch.setattr(agent_router, "run_function_agent", run_agent)
    app.dependency_overrides[get_agent] = lambda: fake_agent

    try:
        response = client.post("/agent/invoke", json={"query": "你好", "session_id": "route-1"})
    finally:
        app.dependency_overrides.pop(get_agent, None)

    assert response.status_code == 200
    assert response.json()["data"]["answer"] == "已完成"
    run_agent.assert_called_once_with("你好", "route-1", agent=fake_agent)
