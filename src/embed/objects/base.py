from typing import Any, Optional
from pydantic import BaseModel


class Document(BaseModel):
    group_key: Optional[str] = "All"
    metadata: Optional[dict] = {}
    text: Optional[list] = []
    embeddings: Optional[list] = []
