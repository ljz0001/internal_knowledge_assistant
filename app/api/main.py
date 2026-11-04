# FastAPI应用的"心脏"，把所有东西组装起来，启动时只需要运行这个文件

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.router import api_router


# 创建FastAPI应用实例
app = FastAPI(
    title="企业内部知识库助手 API",       # Swagger文档里的标题
    description="基于RAG+Agent的企业智能助手系统",  # Swagger文档里的描述
    version="1.0.0",                         # 版本号
    docs_url="/docs",                        # Swagger UI的路径（访问http://localhost:8000/docs ）
    redoc_url="/redoc"                       # 另一种文档格式（ReDoc）的路径
)

# 注册所有业务路由
app.include_router(api_router)


def custom_openapi():
    """修正当前 FastAPI/Pydantic 组合生成的多文件上传 schema。

    新版 OpenAPI 会把 UploadFile 数组表示为 application/octet-stream，
    但当前 Swagger UI 将其显示成字符串输入框。显式使用 binary 后会显示文件选择控件。
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    operation = schema["paths"]["/rag/uploads"]["post"]
    operation["requestBody"] = {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["files"],
                    "properties": {
                        "files": {
                            "type": "array",
                            "description": "选择一个或多个 txt、md、pdf 文件",
                            "items": {"type": "string", "format": "binary"},
                        }
                    },
                }
            }
        },
    }
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# 根路径接口（访问http://localhost:8000/ 时返回）
@app.get("/", summary="根路径健康检查")
async def root():
    return {
        "message": "知识库助手API启动成功！",
        "docs": "访问 http://localhost:8000/docs 查看API文档",
        "version": "1.0.0"
    }



# 直接运行此文件时的启动逻辑（可选，也可以用uvicorn命令）
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" → 允许局域网访问（手机/其他电脑能调）
    # port=8000 → 端口号（改端口就改这里）
    # reload=True → 开发时用，代码改了自动重启（生产环境要关掉，性能好）
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)





