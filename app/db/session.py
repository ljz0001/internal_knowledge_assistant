# sqlalchemy：Python最主流ORM数据库框架，不用手写原生SQL，防止SQL注入
from sqlalchemy import create_engine
# declarative_base：创建所有数据表模型的父类，所有业务表都要继承它
from sqlalchemy.ext.declarative import declarative_base
# sessionmaker：生成数据库会话工厂，会话=和数据库的一次连接通道
from sqlalchemy.orm import sessionmaker
from app.config.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DB
)
# 导入自定义异常，数据库出错统一抛出业务异常，方便接口统一捕获
from app.common.exceptions import MysqlDBException
from urllib.parse import quote_plus

#------------拼接MySQL连接地址----------------
# mysql+pymysql：固定协议标识，pymysql是Python操作MySQL的驱动库
# 格式：账号:密码@数据库IP:端口/数据库名?编码=utf8mb4（支持中文、emoji）
"""
quote_plus() 作用：
把密码里所有特殊字符转换成 URL 安全编码：
@ → %40
: → %3A
/ → %2F
"""
escaped_pwd = quote_plus(MYSQL_PASSWORD)
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{escaped_pwd}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
)

#------------创建数据库引擎engine----------------
# engine = 数据库总连接管理器，全局只创建1个，管控所有数据库连接
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
     # pool_pre_ping=True：每次使用连接前自动ping一下数据库，断线自动重连
    # 解决长时间闲置后MySQL自动断开，程序随机报错问题
    pool_pre_ping=True,
    # pool_size=10：连接池常驻10条连接，多用户同时问答、上传文档复用连接，不用频繁新建销毁
    pool_size=10,
    # max_overflow=20：并发峰值时最多额外扩容20个临时连接，防止大量请求阻塞
    max_overflow=20
)

#------------创建数据库会话工厂SessionLocal----------------
# autocommit=False：默认关闭自动提交，增删改必须手动commit，避免脏数据
# autoflush=False：查询前不自动刷新数据，提升查询速度
# bind=engine：绑定上面创建好的数据库总引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#------------创建数据表模型父类Base----------------
# 所有models下面的数据表模型，都要继承这个Base，才能统一创建数据表
Base = declarative_base()

#------------FastAPI专用依赖函数get_db----------------
# 作用：接口函数直接注入，自动分配数据库会话，用完自动关闭
def get_db():
    # 从会话工厂取出一条数据库连接
    db = SessionLocal()
    try:
         # yield：生成器语法，把会话交给上层接口函数使用
        yield db
    except Exception as e:
        # 任何数据库操作报错，立刻回滚本次事务，防止一半插入一半失败的脏数据
        db.rollback()
        # 抛出自定义业务异常，统一错误码，前端可以识别
        raise MysqlDBException(f"数据库操作异常：{str(e)}")
    finally:
        # 无论成功失败，最终一定会关闭数据库连接，释放连接池资源
        db.close()
