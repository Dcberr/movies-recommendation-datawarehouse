from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ClickEvent:
    session_id: str
    user_id: Optional[int]
    movie_id: Optional[int]
    event_type: str
    query_text: Optional[str]
    source_page: Optional[str]
    event_time: datetime


@dataclass
class RatingEvent:
    user_id: int
    movie_id: int
    rating: float
    source: str = "streamlit"
    event_time: datetime = field(default_factory=datetime.utcnow)
