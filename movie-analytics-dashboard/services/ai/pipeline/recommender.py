# services/ai/pipeline/recommender.py

import pandas as pd

from services.ai.ml.predictor import get_best_model_info, score_candidate_movies
from services.ai.nlp.parser import extract_keywords
from services.ai.mapping.genre_mapper import map_to_valid_genres
from services.ai.repository.movie_repo import (
    get_movies_by_genres,
    get_top_movies
)
from services.ai.ranking.scorer import rank_movies


def build_explanation(row, genres):
    """
    Tạo explain cho UI
    """
    explanation = (
        f"Match {row['match_score']} genres | "
        f"Rating: {row['weighted_rating']:.2f} | "
        f"Votes: {int(row['num_votes'])} | "
        f"Genres: {', '.join(genres)}"
    )
    if "ml_probability" in row and pd.notna(row["ml_probability"]):
        explanation += f" | ML Like: {row['ml_probability']:.1%}"
    if "trending_score" in row and pd.notna(row["trending_score"]):
        explanation += f" | Trending: {row['trending_score']:.2f}"
    return explanation


def enrich_with_hybrid_scores(df: pd.DataFrame):
    if df.empty:
        return df, None

    candidate_df = df.copy()
    if "score" not in candidate_df.columns:
        candidate_df["score"] = candidate_df["weighted_rating"].fillna(0) / 5.0

    candidate_df = candidate_df.rename(columns={"score": "recommendation_score"})

    try:
        scored_df, model_info = score_candidate_movies(candidate_df)
    except Exception:
        scored_df = candidate_df.copy()
        scored_df["ml_probability"] = 0.5
        scored_df["ml_prediction"] = 1
        scored_df["ml_confidence"] = 0.0
        scored_df["best_model"] = "unavailable"
        scored_df["trending_score"] = scored_df.get("trending_score", 0).fillna(0)
        model_info = {
            "model_name": "unavailable",
            "metrics": {},
            "trained_at": None,
        }
    else:
        try:
            best_model_info = get_best_model_info()
        except Exception:
            best_model_info = {"model_name": model_info["model_name"], "metrics": {}, "trained_at": None}
        model_info = best_model_info

    scored_df["recommendation_score"] = scored_df["recommendation_score"].fillna(0.0)
    scored_df["ml_probability"] = scored_df["ml_probability"].fillna(0.5)
    scored_df["trending_score"] = scored_df.get("trending_score", 0).fillna(0.0)
    scored_df["final_score"] = (
        0.5 * scored_df["recommendation_score"]
        + 0.3 * scored_df["ml_probability"]
        + 0.2 * scored_df["trending_score"]
    )
    scored_df = scored_df.sort_values("final_score", ascending=False).reset_index(drop=True)
    return scored_df, model_info


def recommend(user_input: str, top_k: int = 10):
    context = recommend_with_context(user_input, top_k=top_k)
    return context["results"]


def recommend_with_context(user_input: str, top_k: int = 10):
    """
    Main pipeline with diagnostics for UI.
    """

    keywords = extract_keywords(user_input)
    genres = map_to_valid_genres(keywords)

    if not genres:
        df = get_top_movies(limit=top_k)
        df["match_score"] = 0
        df["recommendation_score"] = df["weighted_rating"].fillna(0) / 5.0
        df["reason"] = "Popular movies (no specific genre detected)"
        df, model_info = enrich_with_hybrid_scores(df)

        results = df.to_dict(orient="records")
        return {
            "input": user_input,
            "keywords": keywords,
            "genres": [],
            "fallback_used": True,
            "ml_model": model_info,
            "results": results,
        }

    df = get_movies_by_genres(genres)

    if df.empty:
        return {
            "input": user_input,
            "keywords": keywords,
            "genres": genres,
            "fallback_used": False,
            "results": [],
        }

    df = rank_movies(df, top_k=top_k)

    if df.empty:
        return {
            "input": user_input,
            "keywords": keywords,
            "genres": genres,
            "fallback_used": False,
            "ml_model": None,
            "results": [],
        }

    df, model_info = enrich_with_hybrid_scores(df)
    df["reason"] = df.apply(lambda row: build_explanation(row, genres), axis=1)

    result = df[
        [
            "movie_id",
            "title",
            "avg_rating",
            "year",
            "weighted_rating",
            "num_votes",
            "match_score",
            "recommendation_score",
            "trending_score",
            "ml_probability",
            "ml_prediction",
            "ml_confidence",
            "best_model",
            "final_score",
            "reason"
        ]
    ]

    return {
        "input": user_input,
        "keywords": keywords,
        "genres": genres,
        "fallback_used": False,
        "ml_model": model_info,
        "results": result.to_dict(orient="records"),
    }
