from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.core.config import settings
from app.schemas.chat import SearchDebugResponse, SearchHit


def search_similar_chunks(db: Session, query_emb: list[float], top_k: int, document_ids: Optional[list[str]] = None):
    if document_ids:
        filter_clause = "AND dc.document_id = ANY(:doc_ids)"
    else:
        filter_clause = ""
    sql = text(f"""        SELECT dc.document_id::text, ce.chunk_id::text, dc.chunk_index, 1 - (ce.embedding <=> :qvec) AS similarity, dc.content
        FROM chunk_embeddings ce
        JOIN document_chunks dc ON dc.id = ce.chunk_id
        WHERE 1=1 {filter_clause}
        ORDER BY ce.embedding <=> :qvec
        LIMIT :k
    """ )
    rows = db.execute(sql, {"qvec": query_emb, "k": top_k, "doc_ids": document_ids}).all()
    return rows


def debug_search_chunks(db: Session, query: str, top_k: int = 5) -> SearchDebugResponse:
    from app.rag.embeddings import embed_query
    qv = embed_query(query)
    rows = search_similar_chunks(db, qv, top_k)
    hits: List[SearchHit] = []
    for doc_id, chunk_id, chunk_index, sim, content in rows:
        hits.append(SearchHit(document_id=doc_id, chunk_id=chunk_id, chunk_index=chunk_index, similarity=float(sim), content=content[:500]))
    return SearchDebugResponse(hits=hits)
