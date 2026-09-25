#依赖项

from app.db.session import SessionLocal
from app.agent.function_agent import get_function_agent
from app.config.settings import AGENT_MODE

# ---------- 数据库会话依赖 ----------
def get_db():
    """每次请求自动创建数据库会话，请求结束后自动关闭"""
    db = SessionLocal()  # 创建会话（相当于打开数据库连接）
    try:
        yield db         # yield = 暂停，把db交给路由函数使用
    finally:
        db.close()       # 路由用完后，不管成功失败，这里一定会执行（自动关闭会话）

# ---------- Agent单例依赖 ----------
def get_agent():
    """获取Agent单例（整个程序只初始化一次，避免重复加载模型）"""
    return get_function_agent()

# ---------- Agent模式依赖 ----------
def get_agent_mode():
    """获取当前Agent配置的模式（从settings里读的AGENT_MODE）"""
    return AGENT_MODE