from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 6
    temperature: float = 0.0
    max_tokens: int = 400
    document_ids: Optional[List[str]] = None


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    similarity: float
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]


class SearchHit(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    similarity: float
    content: str


class SearchDebugResponse(BaseModel):
    hits: List[SearchHit]
