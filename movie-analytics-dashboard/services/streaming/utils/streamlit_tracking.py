from datetime import datetime

import pandas as pd
import streamlit as st

from services.streaming.repository.stream_repo import (
    get_latest_click_events,
    get_latest_rating_events,
)
from services.streaming.services.clickstream_service import (
    log_movie_view,
    log_page_visit,
    log_recommendation_click,
    log_search,
)
from services.streaming.services.rating_stream_service import log_rating
from services.streaming.utils.session import generate_session_id, generate_user_id


DEBUG_BUFFER_KEY = "_streaming_debug_events"
SESSION_ID_KEY = "_streaming_session_id"
USER_ID_KEY = "_streaming_user_id"
ACTIVE_PAGE_KEY = "_streaming_active_page"


def ensure_streaming_session():
    if SESSION_ID_KEY not in st.session_state:
        st.session_state[SESSION_ID_KEY] = generate_session_id()

    if USER_ID_KEY not in st.session_state:
        st.session_state[USER_ID_KEY] = generate_user_id()

    if DEBUG_BUFFER_KEY not in st.session_state:
        st.session_state[DEBUG_BUFFER_KEY] = []

    return {
        "session_id": st.session_state[SESSION_ID_KEY],
        "user_id": st.session_state[USER_ID_KEY],
    }


def get_session_id():
    return ensure_streaming_session()["session_id"]


def get_user_id():
    return ensure_streaming_session()["user_id"]


def append_debug_event(event_name, payload, status="success"):
    ensure_streaming_session()
    buffer = st.session_state[DEBUG_BUFFER_KEY]
    buffer.insert(
        0,
        {
            "logged_at": datetime.utcnow(),
            "status": status,
            "event_name": event_name,
            "payload": payload,
        },
    )
    st.session_state[DEBUG_BUFFER_KEY] = buffer[:25]


def show_feedback(message):
    st.toast(message)
    st.success(message)


def show_tracking_error(message, error):
    append_debug_event(
        "tracking_error",
        {
            "message": message,
            "error": str(error),
        },
        status="error",
    )
    st.error(f"{message}: {error}")


def track_page_visit(page_name):
    ensure_streaming_session()
    previous_page = st.session_state.get(ACTIVE_PAGE_KEY)
    if previous_page == page_name:
        return False

    try:
        event = log_page_visit(
            session_id=get_session_id(),
            user_id=get_user_id(),
            source_page=page_name,
        )
        st.session_state[ACTIVE_PAGE_KEY] = page_name
        append_debug_event(
            "open_page",
            {
                "session_id": event.session_id,
                "user_id": event.user_id,
                "source_page": event.source_page,
                "event_time": event.event_time,
            },
        )
        load_latest_click_events.clear()
        return True
    except Exception as error:
        show_tracking_error("Page visit logging failed", error)
        return False


def track_movie_view(movie_id, source_page, success_message="Movie view tracked!"):
    try:
        event = log_movie_view(
            session_id=get_session_id(),
            user_id=get_user_id(),
            movie_id=int(movie_id),
            source_page=source_page,
        )
        append_debug_event(
            "view_movie",
            {
                "session_id": event.session_id,
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "source_page": event.source_page,
                "event_time": event.event_time,
            },
        )
        load_latest_click_events.clear()
        show_feedback(success_message)
        return event
    except Exception as error:
        show_tracking_error("Movie view logging failed", error)
        return None


def track_search(query_text, source_page, success_message="Search event logged!"):
    try:
        event = log_search(
            session_id=get_session_id(),
            user_id=get_user_id(),
            query_text=query_text,
            source_page=source_page,
        )
        if event is None:
            return None

        append_debug_event(
            "search",
            {
                "session_id": event.session_id,
                "user_id": event.user_id,
                "query_text": event.query_text,
                "source_page": event.source_page,
                "event_time": event.event_time,
            },
        )
        load_latest_click_events.clear()
        show_feedback(success_message)
        return event
    except Exception as error:
        show_tracking_error("Search logging failed", error)
        return None


def track_recommendation_click(movie_id, success_message="Recommendation click tracked!"):
    try:
        event = log_recommendation_click(
            session_id=get_session_id(),
            user_id=get_user_id(),
            movie_id=int(movie_id),
        )
        append_debug_event(
            "recommendation_click",
            {
                "session_id": event.session_id,
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "source_page": event.source_page,
                "event_time": event.event_time,
            },
        )
        load_latest_click_events.clear()
        show_feedback(success_message)
        return event
    except Exception as error:
        show_tracking_error("Recommendation click logging failed", error)
        return None


def track_rating(movie_id, rating, source, success_message="Rating streamed successfully!"):
    try:
        event = log_rating(
            user_id=get_user_id(),
            movie_id=int(movie_id),
            rating=float(rating),
            source=source,
        )
        append_debug_event(
            "rating_stream",
            {
                "user_id": event.user_id,
                "movie_id": event.movie_id,
                "rating": event.rating,
                "source": event.source,
                "event_time": event.event_time,
            },
        )
        load_latest_rating_events.clear()
        show_feedback(success_message)
        return event
    except Exception as error:
        show_tracking_error("Rating streaming failed", error)
        return None


def get_debug_buffer_dataframe():
    ensure_streaming_session()
    debug_df = pd.DataFrame(st.session_state[DEBUG_BUFFER_KEY])
    if debug_df.empty:
        return debug_df

    debug_df["logged_at"] = pd.to_datetime(debug_df["logged_at"], errors="coerce")
    return debug_df


@st.cache_data(ttl=5, show_spinner=False)
def load_latest_click_events(limit=10):
    return get_latest_click_events(limit=limit)


@st.cache_data(ttl=5, show_spinner=False)
def load_latest_rating_events(limit=10):
    return get_latest_rating_events(limit=limit)


def render_debug_panel():
    session = ensure_streaming_session()
    with st.expander("Streaming Debug Panel", expanded=False):
        meta_col1, meta_col2 = st.columns(2)
        meta_col1.text_input("Current Session ID", value=session["session_id"], disabled=True)
        meta_col2.text_input("Current User ID", value=str(session["user_id"]), disabled=True)

        st.caption("Latest events logged from this Streamlit session")
        debug_df = get_debug_buffer_dataframe()
        if debug_df.empty:
            st.info("No events have been logged from this session yet.")
        else:
            st.dataframe(debug_df, use_container_width=True, hide_index=True)

        db_col1, db_col2 = st.columns(2)
        with db_col1:
            st.caption("Latest fact_clickstream inserts")
            try:
                click_df = load_latest_click_events(limit=10)
                if click_df.empty:
                    st.info("No clickstream rows found.")
                else:
                    st.dataframe(click_df, use_container_width=True, hide_index=True)
            except Exception as error:
                st.error(f"Unable to load clickstream debug data: {error}")

        with db_col2:
            st.caption("Latest fact_ratings_stream inserts")
            try:
                rating_df = load_latest_rating_events(limit=10)
                if rating_df.empty:
                    st.info("No rating stream rows found.")
                else:
                    st.dataframe(rating_df, use_container_width=True, hide_index=True)
            except Exception as error:
                st.error(f"Unable to load rating stream debug data: {error}")
