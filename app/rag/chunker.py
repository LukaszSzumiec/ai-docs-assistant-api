from app.core.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    size = chunk_size or settings.CHUNK_SIZE
    ovl = overlap or settings.CHUNK_OVERLAP
    tokens = list(text)
    chunks: list[str] = []
    start = 0
    n = len(tokens)
    while start < n:
        end = min(start + size, n)
        chunks.append("".join(tokens[start:end]))
        if end == n:
            break
        start = end - ovl
        if start < 0:
            start = 0
    return chunks
