import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.config.settings import BASE_DIR

# 日志文件夹
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

def get_logger(name: str = "kb_assistant") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # 防止重复添加处理器
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FMT))
    logger.addHandler(console_handler)

    # 文件滚动日志，单文件最大50MB，保留10份
    file_handler = RotatingFileHandler(
        filename=LOG_DIR / "run.log",
        maxBytes=50 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FMT))
    logger.addHandler(file_handler)
    return logger

# 全局日志实例，全项目统一调用
logger = get_logger()