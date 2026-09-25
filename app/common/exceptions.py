class BaseProjectException(Exception):
    """项目统一基础异常，所有业务异常继承此类"""
    code: int
    msg: str

    def __init__(self, msg: str, code: int = 500):
        self.msg = msg
        self.code = code
        super().__init__(self.msg)


# 配置读取异常
class ConfigException(BaseProjectException):
    def __init__(self, msg: str = "配置文件读取/参数缺失异常"):
        super().__init__(msg, code=4001)

# 向量模型加载异常
class EmbeddingException(BaseProjectException):
    def __init__(self, msg: str = "本地Embedding模型加载失败"):
        super().__init__(msg, code=4002)

# Milvus向量库交互异常
class MilvusException(BaseProjectException):
    def __init__(self, msg: str = "Milvus向量数据库操作异常"):
        super().__init__(msg, code=4003)

# 文档解析异常（PDF/Word/TXT读取失败）
class DocumentParseException(BaseProjectException):
    def __init__(self, msg: str = "文档文件解析失败"):
        super().__init__(msg, code=4004)

# MySQL数据库操作异常
class MysqlDBException(BaseProjectException):
    def __init__(self, msg: str = "MySQL数据库读写异常"):
        super().__init__(msg, code=4005)

# LLM大模型调用异常
class LLMServiceException(BaseProjectException):
    def __init__(self, msg: str = "大模型接口调用失败"):
        super().__init__(msg, code=4006)