# services/ai/repository/movie_repo.py

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.db import get_connection


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
        f.weighted_rating,
        f.num_votes
    """

    conn = get_connection()
    df = pd.read_sql(query, conn, params=genres)
    conn.close()

    return df

def get_all_genres():
    query = """
    SELECT genre_name
    FROM dim_genre
    """

    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    return df["genre_name"].tolist()

def get_top_movies(limit=10):
    query = f"""
    SELECT TOP {limit}
        m.movie_id,
        m.title,
        m.year,
        f.weighted_rating,
        f.num_votes
    FROM fact_movie_stats f
    JOIN dim_movie m 
        ON f.movie_id = m.movie_id
    ORDER BY f.weighted_rating DESC
    """

    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()

    return df
