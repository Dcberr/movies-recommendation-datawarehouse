from services.streaming.utils.session import (
    generate_session_id
)

from services.streaming.services.clickstream_service import (
    log_movie_view,
    log_search,
    log_recommendation_click
)

from services.streaming.services.rating_stream_service import (
    log_rating
)


session_id = generate_session_id()

# -----------------------------------------
# CLICK EVENTS
# -----------------------------------------

log_movie_view(
    session_id=session_id,
    movie_id=1
)

log_search(
    session_id=session_id,
    query_text="action comedy"
)

log_recommendation_click(
    session_id=session_id,
    movie_id=10
)

# -----------------------------------------
# RATING EVENT
# -----------------------------------------

log_rating(
    user_id=1,
    movie_id=10,
    rating=5
)

print("Streaming events inserted!")