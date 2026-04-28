# services/ai/pipeline/recommender.py

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
    return (
        f"Match {row['match_score']} genres | "
        f"Rating: {row['weighted_rating']:.2f} | "
        f"Votes: {int(row['num_votes'])} | "
        f"Genres: {', '.join(genres)}"
    )


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
        df["reason"] = "Popular movies (no specific genre detected)"

        results = df.to_dict(orient="records")
        return {
            "input": user_input,
            "keywords": keywords,
            "genres": [],
            "fallback_used": True,
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
            "results": [],
        }

    df["reason"] = df.apply(lambda row: build_explanation(row, genres), axis=1)

    result = df[
        [
            "title",
            "year",
            "weighted_rating",
            "num_votes",
            "match_score",
            "score",
            "reason"
        ]
    ]

    return {
        "input": user_input,
        "keywords": keywords,
        "genres": genres,
        "fallback_used": False,
        "results": result.to_dict(orient="records"),
    }
