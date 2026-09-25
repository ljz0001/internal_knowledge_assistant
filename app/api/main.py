# FastAPI应用的"心脏"，把所有东西组装起来，启动时只需要运行这个文件

from fastapi import FastAPI
#from app.api.router import api_router

from pydantic import BaseModel

# 创建FastAPI应用实例
app = FastAPI(
    title="企业内部知识库助手 API",       # Swagger文档里的标题
    description="基于RAG+Agent的企业智能助手系统",  # Swagger文档里的描述
    version="1.0.0",                         # 版本号
    docs_url="/docs",                        # Swagger UI的路径（访问http://localhost:8000/docs ）
    redoc_url="/redoc"                       # 另一种文档格式（ReDoc）的路径
)

# 注册所有业务路由
#app.include_router(api_router)

# 根路径接口（访问http://localhost:8000/ 时返回）
@app.get("/", summary="根路径健康检查")
async def root():
    return {
        "message": "知识库助手API启动成功！",
        "docs": "访问 http://localhost:8000/docs 查看API文档",
        "version": "1.0.0"
    }



# ---------------- 练习接口开始 ----------------
# GET练习接口：参数从url地址栏获取
@app.get("/demo_get")
async def demo_get(name: str, age: int = 18):
    """
    GET示例
    name：必填参数
    age：选填，默认18
    """
    return {
        "http方法": "GET",
        "你的名字": name,
        "你的年龄": age
    }


# POST需要接收的JSON请求体模型
class DemoPostInput(BaseModel):
    username: str
    question: str
    score: int


# POST练习接口：参数从请求体body获取
@app.post("/demo_post")
async def demo_post(input_data: DemoPostInput):
    """POST示例，数据放在请求体JSON，地址栏看不到"""
    return {
        "http方法": "POST",
        "用户名": input_data.username,
        "提问内容": input_data.question,
        "分数": input_data.score
    }






# 直接运行此文件时的启动逻辑（可选，也可以用uvicorn命令）
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" → 允许局域网访问（手机/其他电脑能调）
    # port=8000 → 端口号（改端口就改这里）
    # reload=True → 开发时用，代码改了自动重启（生产环境要关掉，性能好）
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)





