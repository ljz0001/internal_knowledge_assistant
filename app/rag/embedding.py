from langchain_huggingface import HuggingFaceEmbeddings
from app.config.settings import (
    EMBED_MODEL_NAME,
    EMBED_DEVICE,
    MODEL_ROOT_DIR
)
import os

_embedding_instance: HuggingFaceEmbeddings | None = None

def get_embedding_model() -> HuggingFaceEmbeddings:
    global _embedding_instance
    if _embedding_instance is None:
        # 查找本地已下载的模型路径
        # HuggingFace 缓存格式：models--BAAI--bge-small-zh-v1.5/snapshots/<hash>/
        cache_root = MODEL_ROOT_DIR / f"models--{EMBED_MODEL_NAME.replace('/', '--')}"
        snapshot_dir = None
        if cache_root.exists():
            snapshots = list((cache_root / "snapshots").iterdir())
            if snapshots:
                snapshot_dir = snapshots[0]
        
        if snapshot_dir:
            # 本地有模型，直接加载
            model_path = str(snapshot_dir)
        else:
            # 本地没有，用原始名称（会尝试联网下载）
            model_path = EMBED_MODEL_NAME
        
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs={"device": EMBED_DEVICE},
        )
    return _embedding_instance