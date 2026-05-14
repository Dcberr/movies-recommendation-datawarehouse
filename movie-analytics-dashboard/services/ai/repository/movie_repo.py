# services/ai/repository/movie_repo.py

import sys
from pathlib import Path
import warnings

import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


def read_sql(query, params=None):
    conn = get_connection()
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="pandas only supports SQLAlchemy connectable",
                category=UserWarning,
            )
            return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


def _read_sql_with_connection(conn, query, params=None):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="pandas only supports SQLAlchemy connectable",
            category=UserWarning,
        )
        return pd.read_sql(query, conn, params=params)


def table_exists(table_name: str, conn=None) -> bool:
    query = """
    SELECT COUNT(*) AS table_count
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = ?
    """
    result = _read_sql_with_connection(conn, query, params=[table_name]) if conn else read_sql(query, params=[table_name])
    return bool(int(result.iloc[0]["table_count"]))


def get_table_columns(table_name: str, conn=None) -> list:
    query = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = ?
    ORDER BY ORDINAL_POSITION
    """
    df = _read_sql_with_connection(conn, query, params=[table_name]) if conn else read_sql(query, params=[table_name])
    if df.empty:
        return []
    return df["COLUMN_NAME"].tolist()


def read_table(table_name: str, columns=None, top=None, conn=None) -> pd.DataFrame:
    if not table_exists(table_name, conn=conn):
        return pd.DataFrame()

    available_columns = get_table_columns(table_name, conn=conn)
    if columns:
        selected_columns = [column for column in columns if column in available_columns]
    else:
        selected_columns = available_columns

    if not selected_columns:
        return pd.DataFrame()

    top_clause = f"TOP {int(top)} " if top else ""
    query = f"""
    SELECT {top_clause}{", ".join(selected_columns)}
    FROM {table_name}
    """
    return _read_sql_with_connection(conn, query) if conn else read_sql(query)


def read_many_tables(table_names: list) -> dict:
    conn = get_connection()
    try:
        return {table_name: read_table(table_name, conn=conn) for table_name in table_names}
    finally:
        conn.close()


def get_movies_by_genres(genres: list):
    """
    Lấy phim theo danh sách genre
    Trả về:
    - movie_id
    - title
    - year
    - weighted_rating
    - num_votes
    - match_score (số genre match)
    """

    if not genres:
        return pd.DataFrame()

    # Tạo placeholder cho SQL IN
    placeholders = ",".join(["?"] * len(genres))

    query = f"""
    SELECT 
        m.movie_id,
        m.title,
        m.year,
        f.avg_rating,
        f.weighted_rating,
        f.num_votes,
        COUNT(*) AS match_score
    FROM fact_movie_stats f
    JOIN dim_movie m 
        ON f.movie_id = m.movie_id
    JOIN fact_movie_genre mg 
        ON f.movie_id = mg.movie_id
    JOIN dim_genre g 
        ON mg.genre_id = g.genre_id
    WHERE g.genre_name IN ({placeholders})
    GROUP BY 
        m.movie_id,
        m.title,
        m.year,
        f.avg_rating,
        f.weighted_rating,
        f.num_votes
    """

    return read_sql(query, params=genres)

def get_all_genres():
    query = """
    SELECT genre_name
    FROM dim_genre
    """

    df = read_sql(query)
    return df["genre_name"].tolist()

def get_top_movies(limit=10):
    query = f"""
    SELECT TOP {limit}
        m.movie_id,
        m.title,
        m.year,
        f.avg_rating,
        f.weighted_rating,
        f.num_votes
    FROM fact_movie_stats f
    JOIN dim_movie m 
        ON f.movie_id = m.movie_id
    ORDER BY f.weighted_rating DESC
    """
    return read_sql(query)


def get_candidate_movie_features(movie_ids=None):
    movie_filter = ""
    params = []
    if movie_ids:
        placeholders = ",".join(["?"] * len(movie_ids))
        movie_filter = f"WHERE m.movie_id IN ({placeholders})"
        params = list(movie_ids)

    query = f"""
    WITH genre_stats AS (
        SELECT
            mg.movie_id,
            COUNT(DISTINCT mg.genre_id) AS genres_count,
            MIN(g.genre_name) AS primary_genre
        FROM fact_movie_genre mg
        JOIN dim_genre g
            ON mg.genre_id = g.genre_id
        GROUP BY mg.movie_id
    ),
    clickstream_stats AS (
        SELECT
            c.movie_id,
            COUNT(*) AS total_clicks,
            SUM(CASE WHEN c.event_type = 'recommendation_click' THEN 1 ELSE 0 END) AS recommendation_clicks,
            SUM(CASE WHEN c.event_type = 'search' THEN 1 ELSE 0 END) AS search_count,
            SUM(CASE WHEN c.event_type = 'view_movie' THEN 1 ELSE 0 END) AS views_count,
            SUM(CASE WHEN c.event_type = 'view_movie' AND c.event_time >= DATEADD(HOUR, -24, GETDATE()) THEN 1 ELSE 0 END) AS recent_views
        FROM fact_clickstream c
        GROUP BY c.movie_id
    ),
    rating_stream_stats AS (
        SELECT
            rs.movie_id,
            COUNT(*) AS recent_ratings,
            AVG(CAST(rs.rating AS FLOAT)) AS recent_avg_rating
        FROM fact_ratings_stream rs
        WHERE rs.event_time >= DATEADD(HOUR, -24, GETDATE())
        GROUP BY rs.movie_id
    )
    SELECT
        m.movie_id,
        m.title,
        m.year AS release_year,
        f.avg_rating,
        f.weighted_rating,
        f.num_votes,
        COALESCE(gs.genres_count, 0) AS genres_count,
        COALESCE(gs.primary_genre, 'Unknown') AS primary_genre,
        COALESCE(cs.total_clicks, 0) AS total_clicks,
        COALESCE(cs.recommendation_clicks, 0) AS recommendation_clicks,
        COALESCE(cs.search_count, 0) AS search_count,
        COALESCE(cs.views_count, 0) AS views_count,
        COALESCE(cs.recent_views, 0) AS recent_views,
        COALESCE(rs.recent_ratings, 0) AS recent_ratings,
        COALESCE(rs.recent_avg_rating, 0) AS recent_avg_rating
    FROM dim_movie m
    JOIN fact_movie_stats f
        ON m.movie_id = f.movie_id
    LEFT JOIN genre_stats gs
        ON m.movie_id = gs.movie_id
    LEFT JOIN clickstream_stats cs
        ON m.movie_id = cs.movie_id
    LEFT JOIN rating_stream_stats rs
        ON m.movie_id = rs.movie_id
    {movie_filter}
    """
    return read_sql(query, params=params)
