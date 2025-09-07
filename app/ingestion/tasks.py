from app.core.config import settings
from app.db.base import SessionLocal, engine
from app.db.repositories import set_document_status, upsert_chunks, list_chunk_texts, fetch_chunks_for_embedding
from app.rag.chunker import chunk_text
from app.rag.embeddings import embed_texts
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Public API for router
def enqueue_ingest_document(document_id: str) -> None:
    # If worker is up, send Celery task; otherwise raise to allow sync fallback
    try:
        from app.ingestion.worker import celery_app
        celery_app.send_task("ingest_document", args=[document_id], queue="default")
    except Exception as e:
        raise e


def ingest_document_sync(document_id: str) -> None:
    logger.info("Running sync ingest for document %s", document_id)
    with SessionLocal() as db:
        set_document_status(db, document_id, "processing")
        # 1) read extracted text
        rows = db.execute(text("SELECT extracted_text FROM document_texts WHERE document_id = :id"), {"id": document_id}).all()
        if not rows or not rows[0][0]:
            set_document_status(db, document_id, "failed")
            return
        text_body = rows[0][0]
        # 2) chunk
        chunks = chunk_text(text_body)
        chunk_tuples = [(i, c) for i, c in enumerate(chunks)]
        upsert_chunks(db, document_id, chunk_tuples)
        # 3) embed
        chunk_rows = fetch_chunks_for_embedding(db, document_id)
        vectors = embed_texts([c.content for c in chunk_rows])
        pairs = [(str(c.id), vec) for c, vec in zip(chunk_rows, vectors)]
        with engine.begin() as conn:
            # Bulk insert embeddings
            # Use simple multi-values approach
            conn.exec_driver_sql("DELETE FROM chunk_embeddings WHERE chunk_id = ANY(%s)", ([p[0] for p in pairs],))
            # Build values
            values_sql = ", ".join(["(%s, %s)"] * len(pairs))
            params = []
            for cid, vec in pairs:
                params.extend([cid, vec])
            conn.exec_driver_sql("INSERT INTO chunk_embeddings (chunk_id, embedding) VALUES " + values_sql, params)
        set_document_status(db, document_id, "ready")
