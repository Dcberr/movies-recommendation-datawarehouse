import pyodbc
import pandas as pd

from config.settings import DB_CONFIG


def get_connection():

    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


# ---------------------------------------------------
# CLICKSTREAM
# ---------------------------------------------------

def insert_click_event(event):
    query = """
    INSERT INTO fact_clickstream (
        session_id,
        user_id,
        movie_id,
        event_type,
        query_text,
        source_page,
        event_time
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            query,
            (
                event.session_id,
                event.user_id,
                event.movie_id,
                event.event_type,
                event.query_text,
                event.source_page,
                event.event_time,
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------
# RATING STREAM
# ---------------------------------------------------

def insert_rating_event(event):
    query = """
    INSERT INTO fact_ratings_stream (
        user_id,
        movie_id,
        rating,
        source,
        event_time
    )
    VALUES (?, ?, ?, ?, ?)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            query,
            (
                event.user_id,
                event.movie_id,
                event.rating,
                event.source,
                event.event_time,
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_latest_click_events(limit=20):
    conn = get_connection()
    query = f"""
    SELECT TOP {int(limit)}
        session_id,
        user_id,
        movie_id,
        event_type,
        query_text,
        source_page,
        event_time
    FROM fact_clickstream
    ORDER BY event_time DESC
    """
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def get_latest_rating_events(limit=20):
    conn = get_connection()
    query = f"""
    SELECT TOP {int(limit)}
        user_id,
        movie_id,
        rating,
        source,
        event_time
    FROM fact_ratings_stream
    ORDER BY event_time DESC
    """
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()
