from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from uuid import UUID


class DBId(BaseModel):
    id: UUID


class Meta(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
