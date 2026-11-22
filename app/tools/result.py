"""统一工具结果，供 Agent 稳定判断能力边界和执行结果。"""

from typing import Any, Literal

ToolStatus = Literal["success", "not_found", "unsupported", "invalid_input", "error"]


def tool_result(
    status: ToolStatus,
    *,
    data: Any = None,
    message: str = "",
    code: str = "",
) -> dict[str, Any]:
    return {"status": status, "data": data, "message": message, "code": code}


def success(data: Any = None, message: str = "") -> dict[str, Any]:
    return tool_result("success", data=data, message=message)


def not_found(message: str, data: Any = None) -> dict[str, Any]:
    return tool_result("not_found", data=data, message=message, code="NOT_FOUND")


def unsupported(message: str, code: str = "UNSUPPORTED_OPERATION") -> dict[str, Any]:
    return tool_result("unsupported", message=message, code=code)


def invalid_input(message: str, code: str = "INVALID_INPUT") -> dict[str, Any]:
    return tool_result("invalid_input", message=message, code=code)


def error(message: str, code: str = "TOOL_ERROR") -> dict[str, Any]:
    return tool_result("error", message=message, code=code)
