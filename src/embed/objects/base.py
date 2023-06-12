from typing import Optional

from pydantic import BaseModel


class Document(BaseModel):
    group_key: Optional[str] = "All"
    metadata: Optional[dict] = {}
    text: Optional[list] = []
    embeddings: Optional[list] = []


class Image(BaseModel):
    group_key: Optional[str] = 'All'
    metadata: Optional[dict] = {}
    image: Any
    embeddings: Optional[list] = []
