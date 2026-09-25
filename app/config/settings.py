import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent

# 加载.env
load_dotenv(BASE_DIR/".env")

# 读
with open(BASE_DIR/"app/config/config.yaml","r",encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

#--------------路径全局常量----------------
DOCS_DIR = BASE_DIR / CONFIG["base"]["docs_dir"]
UPLOADS_DIR = BASE_DIR / CONFIG["base"]["uploads_dir"]
CACHE_DIR = BASE_DIR / CONFIG["base"]["cache_dir"]
MODEL_ROOT_DIR = BASE_DIR / CONFIG["base"]["model_dir"]

# 自动创建所有业务文件夹
for dir_path in [DOCS_DIR, UPLOADS_DIR, CACHE_DIR, MODEL_ROOT_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

#--------------Milvus向量库配置----------------
MILVUS_HOST = CONFIG["milvus"]["host"]
MILVUS_PORT = CONFIG["milvus"]["port"]
MILVUS_COLLECTION_NAME = CONFIG["milvus"]["collection_name"]

#--------------Chroma向量库配置----------------
CHROMA_PERSIST_DIR = CONFIG["chroma"]["persist_dir"]



#--------------Rag模型配置----------------
CHUNK_SIZE = CONFIG["rag"]["chunk_size"]
CHUNK_OVERLAP = CONFIG["rag"]["chunk_overlap"]
RECALL_TOP_K = CONFIG["rag"]["top_k"]
ENABLE_RERANK = CONFIG["rerank_enable"]

#--------------向量模型配置----------------
EMBED_MODEL_NAME = CONFIG["embedding"]["model_name"]
EMBED_DEVICE = CONFIG["embedding"]["device"]

#--------------重排序模型配置----------------
RERANK_MODEL_NAME = CONFIG["rerank"]["model_name"]
RERANK_DEVICE = CONFIG["rerank"]["device"]
RERANK_USE_FP16 = CONFIG["rerank"]["use_fp16"]

#--------------MySQL数据库配置----------------
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PWD")
MYSQL_DB = os.getenv("MYSQL_DB")

#--------------大模型配置----------------
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
LLM_TEMPERATURE = float(os.getenv("TEMPERATURE"))

AGENT_MODE = CONFIG.get("agent", {}).get("mode", "function")
