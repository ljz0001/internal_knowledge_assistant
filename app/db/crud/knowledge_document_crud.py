"""知识库文件记录的数据库操作；本模块不操作磁盘或向量库。"""

from sqlalchemy.orm import Session

from app.db.models.knowledge_document import KnowledgeDocument


def create_document(db: Session, document_info: dict) -> KnowledgeDocument:
    document = KnowledgeDocument(**document_info)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document_by_id(db: Session, document_id: int) -> KnowledgeDocument | None:
    return db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()


def get_document_by_hash(db: Session, file_hash: str, statuses: list[str] | None = None) -> KnowledgeDocument | None:
    query = db.query(KnowledgeDocument).filter(KnowledgeDocument.file_hash == file_hash)
    if statuses:
        query = query.filter(KnowledgeDocument.status.in_(statuses))
    return query.first()


def list_documents(db: Session, status: str | None = None) -> list[KnowledgeDocument]:
    query = db.query(KnowledgeDocument)
    if status:
        query = query.filter(KnowledgeDocument.status == status)
    return query.order_by(KnowledgeDocument.create_time.desc(), KnowledgeDocument.id.desc()).all()


def update_document(db: Session, document_id: int, update_data: dict) -> KnowledgeDocument | None:
    document = get_document_by_id(db, document_id)
    if not document:
        return None
    for key, value in update_data.items():
        setattr(document, key, value)
    db.commit()
    db.refresh(document)
    return document
