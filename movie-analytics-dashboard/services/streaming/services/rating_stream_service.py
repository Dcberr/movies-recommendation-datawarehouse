from datetime import datetime

from services.streaming.models.event_model import RatingEvent

from services.streaming.repository.stream_repo import (
    insert_rating_event
)


def log_rating(
    user_id,
    movie_id,
    rating,
    source="streamlit"
):
    event = RatingEvent(
        user_id=user_id,
        movie_id=movie_id,
        rating=rating,
        source=source,
        event_time=datetime.utcnow(),
    )
    insert_rating_event(event)
    return event
