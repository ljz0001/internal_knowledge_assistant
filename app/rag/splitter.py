from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

def get_text_splitter() -> RecursiveCharacterTextSplitter:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )
    return splitter