# services/ai/ranking/scorer.py

import numpy as np
import pandas as pd
from services.ai.config.constants import SCORING_WEIGHTS, TOP_K


def normalize(series: pd.Series) -> pd.Series:
    if series.max() == series.min():
        return pd.Series([0.5] * len(series))
    return (series - series.min()) / (series.max() - series.min())


def compute_imdb_score(df: pd.DataFrame) -> pd.Series:
    """
    IMDb weighted rating
    """
    C = df["weighted_rating"].mean()

    # đảm bảo threshold đủ lớn để penalize low-vote
    m = max(1000, df["num_votes"].quantile(0.75))

    v = df["num_votes"]
    R = df["weighted_rating"]

    return (v / (v + m)) * R + (m / (v + m)) * C


def match_weight(ms, max_ms):
    if ms == max_ms:
        return 1.0
    elif ms == max_ms - 1:
        return 0.95   # 🔥 giảm chênh lệch
    else:
        return 0.9


def compute_score(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    # 1. FILTER theo intent
    max_ms = df["match_score"].max()
    df = df[df["match_score"] >= max_ms - 1]

    # 2. FILTER vote cứng (quan trọng)
    df = df[df["num_votes"] >= 50]

    if df.empty:
        return df

    # 3. MATCH boost (nhẹ thôi)
    max_ms = df["match_score"].max()
    df["match_boost"] = df["match_score"].apply(lambda x: match_weight(x, max_ms))

    # 4. RATING
    df["imdb_score"] = compute_imdb_score(df)
    df["scaled_rating"] = df["imdb_score"] / 5.0

    # 5. VOTES
    df["vote_score"] = normalize(np.log1p(df["num_votes"]))

    # 6. FINAL SCORE (rating là chính)
    df["score"] = (
        0.2 * df["match_boost"]
        + 0.6 * df["scaled_rating"]
        + 0.2 * df["vote_score"]
    )

    return df


def rank_movies(df: pd.DataFrame, top_k: int = TOP_K) -> pd.DataFrame:
    if df.empty:
        return df

    df = compute_score(df)

    # --------------------------------------------------
    # 8. SORT chuẩn production
    # --------------------------------------------------
    df = df.sort_values("score", ascending=False)

    return df.head(top_k)