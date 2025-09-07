from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from typing import Sequence


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    emb = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY, model=settings.EMBEDDING_MODEL)
    # LangChain handles batching internally
    vectors = emb.embed_documents(list(texts))
    return vectors


def embed_query(text: str) -> list[float]:
    emb = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY, model=settings.EMBEDDING_MODEL)
    return emb.embed_query(text)
