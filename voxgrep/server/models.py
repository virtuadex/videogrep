from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class VideoBase(SQLModel):
    path: str = Field(index=True, unique=True)
    filename: str
    size_bytes: int
    duration: float = 0.0
    created_at: float
    has_transcript: bool = False
    transcript_path: Optional[str] = None

class Video(VideoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # ngrams: List["NGram"] = Relationship(back_populates="video")

class SearchResult(SQLModel):
    file: str
    start: float
    end: float
    content: str
    score: Optional[float] = None
