from pydantic import BaseModel
from typing import List, Optional

class Chunk(BaseModel):
    page_number: int
    page_content: str

class ProcessedDocument(BaseModel):
    filename: str
    candidate_id: str
    structured_data: dict
    chunks: Optional[List[Chunk]] = None