from pydantic import BaseModel
from typing import List


class GlossaryItem(BaseModel):
    term: str
    definition: str
    example: str


class SourceInfo(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class GlossaryResponse(BaseModel):
    source: SourceInfo
    model: str
    n_terms_requested: int
    terms_returned: int
    text_chars_sent: int
    items: List[GlossaryItem]