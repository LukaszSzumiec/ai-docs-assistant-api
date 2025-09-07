from pydantic import BaseModel
from uuid import UUID


class DocumentCreateResponse(BaseModel):
    document_id: UUID


class DocumentStatusResponse(BaseModel):
    document_id: str
    status: str
