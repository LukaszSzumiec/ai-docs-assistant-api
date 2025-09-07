from sqlalchemy.orm import Session
from app.db.models import Document, DocumentText, DocumentChunk, ChunkEmbedding
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update, delete


def create_document_stub(db: Session, filename: str, mime_type: str, extracted_text: str, metadata: dict | None):
    doc = Document(filename=filename, mime_type=mime_type, metadata=metadata, status="uploaded")
    db.add(doc)
    db.flush()
    db.add(DocumentText(document_id=doc.id, extracted_text=extracted_text))
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, document_id: str) -> Optional[Document]:
    return db.get(Document, UUID(document_id))


def set_document_status(db: Session, document_id: str, status: str) -> None:
    db.execute(update(Document).where(Document.id == UUID(document_id)).values(status=status))
    db.commit()


def upsert_chunks(db: Session, document_id: str, chunks: list[tuple[int, str]]):
    # chunks: list of (chunk_index, content)
    # Drop old
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == UUID(document_id)))
    for idx, content in chunks:
        db.add(DocumentChunk(document_id=UUID(document_id), chunk_index=idx, content=content))
    db.commit()


def fetch_chunks_for_embedding(db: Session, document_id: str) -> list[DocumentChunk]:
    rows = db.scalars(select(DocumentChunk).where(DocumentChunk.document_id == UUID(document_id)).order_by(DocumentChunk.chunk_index)).all()
    return rows


def list_chunk_texts(db: Session, document_id: str) -> list[tuple[str, str]]:
    rows = db.execute(
        select(DocumentChunk.id, DocumentChunk.content).where(DocumentChunk.document_id == UUID(document_id))
    ).all()
    return [(str(r[0]), r[1]) for r in rows]
