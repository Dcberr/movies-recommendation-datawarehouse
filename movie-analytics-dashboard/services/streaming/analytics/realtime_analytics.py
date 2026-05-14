import pandas as pd

from services.streaming.repository.stream_repo import (
    get_connection
)


# ---------------------------------------------------
# TRENDING MOVIES
# ---------------------------------------------------

def get_trending_movies(minutes=5, top_k=10):

    conn = get_connection()

    query = f"""
    SELECT TOP {top_k}

        m.title,

        COUNT(*) AS total_views,

        AVG(CAST(s.rating AS FLOAT)) AS avg_rating

    FROM fact_ratings_stream s

    JOIN dim_movie m
        ON s.movie_id = m.movie_id

    WHERE s.event_time >= DATEADD(MINUTE, -{minutes}, GETDATE())

    GROUP BY m.title

    ORDER BY total_views DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ---------------------------------------------------
# HOT GENRES
# ---------------------------------------------------

def get_hot_genres(minutes=5):

    conn = get_connection()

    query = f"""
    SELECT TOP 10

        g.genre_name,

        COUNT(*) AS total_events

    FROM fact_clickstream c

    JOIN fact_movie_genre mg
        ON c.movie_id = mg.movie_id

    JOIN dim_genre g
        ON mg.genre_id = g.genre_id

    WHERE c.event_time >= DATEADD(MINUTE, -{minutes}, GETDATE())

    GROUP BY g.genre_name

    ORDER BY total_events DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ---------------------------------------------------
# ACTIVE USERS
# ---------------------------------------------------

def get_active_users(minutes=5):

    conn = get_connection()

    query = f"""
    SELECT

        COUNT(DISTINCT session_id) AS active_sessions,

        COUNT(DISTINCT user_id) AS active_users

    FROM fact_clickstream

    WHERE event_time >= DATEADD(MINUTE, -{minutes}, GETDATE())
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df.iloc[0].to_dict()


# ---------------------------------------------------
# LIVE SEARCHES
# ---------------------------------------------------

def get_live_searches(minutes=5, top_k=10):

    conn = get_connection()

    query = f"""
    SELECT TOP {top_k}

        query_text,

        COUNT(*) AS total_searches

    FROM fact_clickstream

    WHERE event_type = 'search'

    AND query_text IS NOT NULL

    AND event_time >= DATEADD(MINUTE, -{minutes}, GETDATE())

    GROUP BY query_text

    ORDER BY total_searches DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ---------------------------------------------------
# LIVE EVENTS FEED
# ---------------------------------------------------

def get_live_events(limit=20):

    conn = get_connection()

    query = f"""
    SELECT TOP {limit}

        event_type,
        movie_id,
        query_text,
        source_page,
        event_time

    FROM fact_clickstream

    ORDER BY event_time DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df