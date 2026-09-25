import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain_core.documents import Document
from app.config.settings import MODEL_ROOT_DIR, RERANK_MODEL_NAME, RERANK_DEVICE

_reranker_instance = None
_tokenizer_instance = None

def _get_model_and_tokenizer():
    global _reranker_instance, _tokenizer_instance
    if _reranker_instance is None:
        cache_root = MODEL_ROOT_DIR / f"models--{RERANK_MODEL_NAME.replace('/', '--')}"
        snapshot_dir = None
        if cache_root.exists():
            snapshots = list((cache_root / "snapshots").iterdir())
            if snapshots:
                snapshot_dir = snapshots[0]
        model_path = str(snapshot_dir) if snapshot_dir else RERANK_MODEL_NAME
        
        _tokenizer_instance = AutoTokenizer.from_pretrained(model_path)
        _reranker_instance = AutoModelForSequenceClassification.from_pretrained(model_path)
        _reranker_instance.to(RERANK_DEVICE)
        _reranker_instance.eval()
    return _reranker_instance, _tokenizer_instance

def rerank_documents(query: str, documents: list[Document], top_k: int = 4) -> list[Document]:
    if not documents:
        return []
    
    model, tokenizer = _get_model_and_tokenizer()
    pairs = [(query, doc.page_content) for doc in documents]
    
    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(RERANK_DEVICE)
    
    with torch.no_grad():
        outputs = model(**inputs)
        scores = outputs.logits.squeeze().cpu().numpy()
    
    for i, doc in enumerate(documents):
        doc.metadata["rerank_score"] = float(scores[i])
    
    documents.sort(key=lambda d: d.metadata["rerank_score"], reverse=True)
    return documents[:top_k]