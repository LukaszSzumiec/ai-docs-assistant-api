from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Optional
from app.api.deps import get_db, require_api_key
from sqlalchemy.orm import Session
from app.schemas.documents import DocumentCreateResponse, DocumentStatusResponse
from app.schemas.chat import ChatRequest, ChatResponse, SearchDebugResponse
from app.db.repositories import (
    create_document_stub, get_document, set_document_status,
)
from app.ingestion.parsers import extract_text_from_upload
from app.ingestion.tasks import enqueue_ingest_document, ingest_document_sync
from app.rag.pipeline import answer_query
from app.rag.retriever import debug_search_chunks

api_router = APIRouter(dependencies=[Depends(require_api_key)])


@api_router.post("/documents/upload", response_model=DocumentCreateResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_bytes = await file.read()
    text, meta = extract_text_from_upload(raw_bytes, file.filename, file.content_type)
    doc = create_document_stub(db, filename=file.filename, mime_type=file.content_type, extracted_text=text, metadata=meta)
    # enqueue async ingest (Celery); fallback: sync (dev)
    try:
        enqueue_ingest_document(str(doc.id))
    except Exception:
        ingest_document_sync(str(doc.id))
    return DocumentCreateResponse(document_id=doc.id)


@api_router.post("/documents/{document_id}/ingest", response_model=DocumentStatusResponse)
def trigger_ingest(document_id: str, db: Session = Depends(get_db)):
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    set_document_status(db, document_id, "processing")
    try:
        enqueue_ingest_document(document_id)
    except Exception:
        ingest_document_sync(document_id)
    return DocumentStatusResponse(document_id=document_id, status="processing")


@api_router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
def document_status(document_id: str, db: Session = Depends(get_db)):
    doc = get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    return DocumentStatusResponse(document_id=document_id, status=doc.status)


@api_router.post("/chat/query", response_model=ChatResponse)
def chat_query(payload: ChatRequest, db: Session = Depends(get_db)):
    return answer_query(db, payload)


@api_router.get("/chunks/search", response_model=SearchDebugResponse)
def chunks_search_debug(q: str, top_k: Optional[int] = 5, db: Session = Depends(get_db)):
    return debug_search_chunks(db, query=q, top_k=top_k or 5)
