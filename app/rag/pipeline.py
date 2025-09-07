from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.core.config import settings
from app.rag.retriever import search_similar_chunks
from app.rag.prompt import SYSTEM_PROMPT, build_prompt
from langchain_openai import ChatOpenAI


def answer_query(db: Session, payload: ChatRequest) -> ChatResponse:
    from app.rag.embeddings import embed_query

    qv = embed_query(payload.query)
    rows = search_similar_chunks(db, qv, payload.top_k, payload.document_ids)
    contexts = []
    citations: list[Citation] = []
    for doc_id, chunk_id, chunk_index, sim, content in rows:
        contexts.append(content)
        citations.append(
            Citation(
                document_id=doc_id,
                chunk_id=chunk_id,
                chunk_index=int(chunk_index),
                similarity=float(sim),
                snippet=content[:200],
            )
        )

    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=settings.CHAT_MODEL, temperature=payload.temperature, max_tokens=payload.max_tokens)
    prompt = build_prompt(payload.query, contexts)
    resp = llm.invoke([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
    answer = resp.content if hasattr(resp, "content") else str(resp)

    return ChatResponse(answer=answer, citations=citations)
