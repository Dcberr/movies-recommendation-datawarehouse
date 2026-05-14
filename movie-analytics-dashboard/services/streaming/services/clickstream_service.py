from datetime import datetime

from services.streaming.models.event_model import ClickEvent

from services.streaming.repository.stream_repo import (
    insert_click_event
)


def _build_click_event(
    session_id,
    event_type,
    user_id=None,
    movie_id=None,
    query_text=None,
    source_page=None,
):
    return ClickEvent(
        session_id=session_id,
        user_id=user_id,
        movie_id=movie_id,
        event_type=event_type,
        query_text=query_text,
        source_page=source_page,
        event_time=datetime.utcnow(),
    )


def log_page_visit(
    session_id,
    user_id=None,
    source_page="dashboard",
):
    event = _build_click_event(
        session_id=session_id,
        user_id=user_id,
        event_type="open_page",
        source_page=source_page,
    )
    insert_click_event(event)
    return event


def log_movie_view(
    session_id,
    movie_id,
    user_id=None,
    source_page="dashboard"
):
    event = _build_click_event(
        session_id=session_id,
        user_id=user_id,
        movie_id=movie_id,
        event_type="view_movie",
        source_page=source_page,
    )
    insert_click_event(event)
    return event


def log_search(
    session_id,
    query_text,
    user_id=None,
    source_page="recommendation"
):
    cleaned_query = (query_text or "").strip()
    if not cleaned_query:
        return None

    event = _build_click_event(
        session_id=session_id,
        user_id=user_id,
        event_type="search",
        query_text=cleaned_query,
        source_page=source_page,
    )
    insert_click_event(event)
    return event


def log_recommendation_click(
    session_id,
    movie_id,
    user_id=None
):
    event = _build_click_event(
        session_id=session_id,
        user_id=user_id,
        movie_id=movie_id,
        event_type="recommendation_click",
        source_page="recommendation",
    )
    insert_click_event(event)
    return event
