import numpy as np

from services.streaming.analytics.realtime_analytics import (
    get_trending_movies
)


def compute_trending_scores(minutes=10):

    df = get_trending_movies(minutes=minutes)

    if df.empty:
        return df

    # normalize views
    max_views = df["total_views"].max()

    df["view_score"] = (
        df["total_views"] / max_views
    )

    # normalize rating
    if "avg_rating" in df.columns:
        df["rating_score"] = (
            df["avg_rating"].fillna(0) / 5.0
        )
    else:
        df["rating_score"] = 0

    # hybrid trending score
    df["trending_score"] = (
        0.7 * df["view_score"]
        + 0.3 * df["rating_score"]
    )

    return df.sort_values(
        "trending_score",
        ascending=False
    )