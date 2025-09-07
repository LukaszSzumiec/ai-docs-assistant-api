from typing import Tuple, Dict, Any
from pypdf import PdfReader
import io


def extract_text_from_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def extract_text_from_upload(raw: bytes, filename: str, mime_type: str | None) -> Tuple[str, Dict[str, Any]]:
    meta = {"filename": filename, "mime_type": mime_type}
    if mime_type and "pdf" in mime_type.lower():
        return extract_text_from_pdf(raw), meta
    # Fallback: treat as utf-8 text
    try:
        return raw.decode("utf-8"), meta
    except Exception:
        return "", meta
