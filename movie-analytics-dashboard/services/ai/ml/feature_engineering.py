from dataclasses import dataclass
import warnings

import numpy as np
import pandas as pd

from services.ai.ml.utils import TARGET_COLUMN, normalize_series
from services.ai.repository.movie_repo import (
    get_candidate_movie_features,
    read_table,
)


LOOKBACK_HOURS = 24
COUNT_FEATURES = [
    "num_votes",
    "genres_count",
    "total_clicks",
    "recommendation_clicks",
    "search_count",
    "views_count",
    "recent_views",
    "recent_ratings",
]


@dataclass
class FeatureSet:
    dataframe: pd.DataFrame
    numeric_features: list
    categorical_features: list
    target_column: str = TARGET_COLUMN


def _standardize_column_types(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    standardized = df.copy()
    for column in ("movie_id", "user_id"):
        if column in standardized.columns:
            standardized[column] = pd.to_numeric(standardized[column], errors="coerce")

    for column in ("rating", "avg_rating", "weighted_rating", "num_votes", "year"):
        if column in standardized.columns:
            standardized[column] = pd.to_numeric(standardized[column], errors="coerce")

    return standardized


def _sanitize_numeric_features(dataset: pd.DataFrame, numeric_features: list) -> pd.DataFrame:
    if dataset.empty:
        return dataset

    sanitized = dataset.copy()

    for feature in numeric_features:
        if feature not in sanitized.columns:
            sanitized[feature] = np.nan
            continue
        sanitized[feature] = pd.to_numeric(sanitized[feature], errors="coerce")

    bounded_ranges = {
        "avg_rating": (0.0, 5.0),
        "weighted_rating": (0.0, 5.0),
        "recent_avg_rating": (0.0, 5.0),
        "trending_score": (0.0, 1.0),
        "release_year": (1880.0, 2100.0),
    }

    for feature, (lower, upper) in bounded_ranges.items():
        if feature in sanitized.columns:
            sanitized[feature] = sanitized[feature].clip(lower=lower, upper=upper)

    for feature in COUNT_FEATURES:
        if feature in sanitized.columns:
            sanitized[feature] = sanitized[feature].clip(lower=0)
            sanitized[feature] = np.log1p(sanitized[feature])

    for feature in numeric_features:
        if feature not in sanitized.columns:
            continue
        sanitized[feature] = sanitized[feature].replace([np.inf, -np.inf], np.nan)
        valid_values = sanitized[feature].dropna()
        if valid_values.empty:
            continue
        lower_bound = valid_values.quantile(0.01)
        upper_bound = valid_values.quantile(0.99)
        if pd.notna(lower_bound) and pd.notna(upper_bound) and lower_bound <= upper_bound:
            sanitized[feature] = sanitized[feature].clip(lower=lower_bound, upper=upper_bound)

    return sanitized


def _prepare_genre_features(movie_genre_df: pd.DataFrame, dim_genre_df: pd.DataFrame) -> pd.DataFrame:
    if movie_genre_df.empty or dim_genre_df.empty:
        return pd.DataFrame(columns=["movie_id", "genres_count", "primary_genre"])

    merged = movie_genre_df.merge(dim_genre_df, on="genre_id", how="left")
    merged["genre_name"] = merged["genre_name"].fillna("Unknown")

    aggregated = (
        merged.groupby("movie_id")
        .agg(
            genres_count=("genre_id", "nunique"),
            primary_genre=("genre_name", lambda values: sorted(set(values))[0] if len(values) else "Unknown"),
        )
        .reset_index()
    )
    return aggregated


def _prepare_behavior_features(
    clickstream_df: pd.DataFrame,
    behavior_df: pd.DataFrame,
) -> pd.DataFrame:
    frames = []

    if not clickstream_df.empty and "movie_id" in clickstream_df.columns:
        clickstream = clickstream_df.copy()
        clickstream["event_type"] = clickstream["event_type"].fillna("unknown")

        click_agg = (
            clickstream.groupby("movie_id")
            .agg(
                total_clicks=("event_type", "size"),
                recommendation_clicks=("event_type", lambda values: int((values == "recommendation_click").sum())),
                search_count=("event_type", lambda values: int((values == "search").sum())),
                views_count=("event_type", lambda values: int((values == "view_movie").sum())),
            )
            .reset_index()
        )
        frames.append(click_agg)

    if not behavior_df.empty and "movie_id" in behavior_df.columns:
        candidate_columns = {
            "total_clicks": [column for column in behavior_df.columns if column.lower() == "total_clicks"],
            "recommendation_clicks": [column for column in behavior_df.columns if column.lower() == "recommendation_clicks"],
            "search_count": [column for column in behavior_df.columns if column.lower() == "search_count"],
            "views_count": [column for column in behavior_df.columns if column.lower() == "views_count"],
        }

        available_aggregations = {}
        for output_column, matched_columns in candidate_columns.items():
            if matched_columns:
                available_aggregations[output_column] = (matched_columns[0], "sum")

        if available_aggregations:
            behavior_agg = behavior_df.groupby("movie_id").agg(**available_aggregations).reset_index()
            frames.append(behavior_agg)

    if not frames:
        return pd.DataFrame(columns=["movie_id", "total_clicks", "recommendation_clicks", "search_count", "views_count"])

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="movie_id", how="outer", suffixes=("", "_behavior"))

    for metric in ("total_clicks", "recommendation_clicks", "search_count", "views_count"):
        behavior_column = f"{metric}_behavior"
        if behavior_column in merged.columns:
            merged[metric] = merged.get(metric, 0).fillna(0) + merged[behavior_column].fillna(0)
            merged = merged.drop(columns=[behavior_column])
        elif metric not in merged.columns:
            merged[metric] = 0

    return merged


def _prepare_realtime_features(
    clickstream_df: pd.DataFrame,
    ratings_stream_df: pd.DataFrame,
) -> pd.DataFrame:
    realtime_df = pd.DataFrame(columns=["movie_id", "recent_views", "recent_ratings", "recent_avg_rating", "trending_score"])

    if not clickstream_df.empty and "movie_id" in clickstream_df.columns:
        clickstream = clickstream_df.copy()
        if "event_time" in clickstream.columns:
            clickstream["event_time"] = pd.to_datetime(clickstream["event_time"], errors="coerce")
            cutoff = clickstream["event_time"].max() - pd.Timedelta(hours=LOOKBACK_HOURS)
            clickstream = clickstream[clickstream["event_time"].isna() | (clickstream["event_time"] >= cutoff)]

        recent_views = (
            clickstream.assign(
                view_indicator=lambda frame: (frame["event_type"] == "view_movie").astype(int)
            )
            .groupby("movie_id")
            .agg(recent_views=("view_indicator", "sum"))
            .reset_index()
        )
        realtime_df = recent_views

    if not ratings_stream_df.empty and "movie_id" in ratings_stream_df.columns:
        ratings_stream = ratings_stream_df.copy()
        if "event_time" in ratings_stream.columns:
            ratings_stream["event_time"] = pd.to_datetime(ratings_stream["event_time"], errors="coerce")
            cutoff = ratings_stream["event_time"].max() - pd.Timedelta(hours=LOOKBACK_HOURS)
            ratings_stream = ratings_stream[ratings_stream["event_time"].isna() | (ratings_stream["event_time"] >= cutoff)]

        rating_agg = (
            ratings_stream.groupby("movie_id")
            .agg(
                recent_ratings=("rating", "size"),
                recent_avg_rating=("rating", "mean"),
            )
            .reset_index()
        )
        realtime_df = realtime_df.merge(rating_agg, on="movie_id", how="outer")

    if realtime_df.empty:
        return pd.DataFrame(columns=["movie_id", "recent_views", "recent_ratings", "recent_avg_rating", "trending_score"])

    realtime_df["recent_views"] = realtime_df.get("recent_views", 0).fillna(0)
    realtime_df["recent_ratings"] = realtime_df.get("recent_ratings", 0).fillna(0)
    realtime_df["recent_avg_rating"] = realtime_df.get("recent_avg_rating", 0).fillna(0.0)
    realtime_df["view_score"] = normalize_series(realtime_df["recent_views"])
    realtime_df["rating_score"] = realtime_df["recent_avg_rating"].clip(lower=0, upper=5) / 5.0
    realtime_df["trending_score"] = 0.7 * realtime_df["view_score"] + 0.3 * realtime_df["rating_score"]

    return realtime_df.drop(columns=["view_score", "rating_score"])


def load_training_frames() -> dict:
    warnings.filterwarnings(
        "ignore",
        message="pandas only supports SQLAlchemy connectable",
        category=UserWarning,
    )
    frames = {
        "fact_ratings": read_table(
            "fact_ratings",
            columns=["user_id", "movie_id", "rating"],
        ),
        "fact_movie_stats": read_table(
            "fact_movie_stats",
            columns=["movie_id", "avg_rating", "weighted_rating", "num_votes"],
        ),
        "dim_movie": read_table(
            "dim_movie",
            columns=["movie_id", "title", "year"],
        ),
        "fact_user_behavior": read_table(
            "fact_user_behavior",
            columns=["user_id", "movie_id", "total_clicks", "recommendation_clicks", "search_count", "views_count"],
        ),
        "fact_movie_genre": read_table(
            "fact_movie_genre",
            columns=["movie_id", "genre_id"],
        ),
        "dim_genre": read_table(
            "dim_genre",
            columns=["genre_id", "genre_name"],
        ),
        "fact_clickstream": read_table(
            "fact_clickstream",
            columns=["movie_id", "event_type", "event_time"],
        ),
        "fact_ratings_stream": read_table(
            "fact_ratings_stream",
            columns=["movie_id", "rating", "event_time"],
        ),
    }
    return {name: _standardize_column_types(df) for name, df in frames.items()}


def build_movie_feature_frame(frames: dict) -> pd.DataFrame:
    ratings_df = frames.get("fact_ratings", pd.DataFrame())
    movie_stats_df = frames.get("fact_movie_stats", pd.DataFrame())
    dim_movie_df = frames.get("dim_movie", pd.DataFrame())
    behavior_df = frames.get("fact_user_behavior", pd.DataFrame())
    movie_genre_df = frames.get("fact_movie_genre", pd.DataFrame())
    dim_genre_df = frames.get("dim_genre", pd.DataFrame())
    clickstream_df = frames.get("fact_clickstream", pd.DataFrame())
    ratings_stream_df = frames.get("fact_ratings_stream", pd.DataFrame())

    if ratings_df.empty or movie_stats_df.empty or dim_movie_df.empty:
        return pd.DataFrame()

    movie_features = ratings_df[["user_id", "movie_id", "rating"]].copy()
    movie_features = movie_features.merge(movie_stats_df, on="movie_id", how="left")
    movie_features = movie_features.merge(dim_movie_df[["movie_id", "year"]], on="movie_id", how="left")

    genre_features = _prepare_genre_features(movie_genre_df, dim_genre_df)
    behavior_features = _prepare_behavior_features(clickstream_df, behavior_df)
    realtime_features = _prepare_realtime_features(clickstream_df, ratings_stream_df)

    movie_features = movie_features.merge(genre_features, on="movie_id", how="left")
    movie_features = movie_features.merge(behavior_features, on="movie_id", how="left")
    movie_features = movie_features.merge(realtime_features, on="movie_id", how="left")

    movie_features["like"] = (movie_features["rating"] >= 4).astype(int)
    movie_features = movie_features.rename(columns={"year": "release_year"})

    for column in (
        "genres_count",
        "total_clicks",
        "recommendation_clicks",
        "search_count",
        "views_count",
        "recent_views",
        "recent_ratings",
        "recent_avg_rating",
        "trending_score",
    ):
        if column not in movie_features.columns:
            movie_features[column] = 0

    if "primary_genre" not in movie_features.columns:
        movie_features["primary_genre"] = "Unknown"

    movie_features["primary_genre"] = movie_features["primary_genre"].fillna("Unknown")
    movie_features["release_year"] = pd.to_numeric(movie_features["release_year"], errors="coerce")

    return movie_features


def build_training_dataset() -> FeatureSet:
    frames = load_training_frames()
    dataset = build_movie_feature_frame(frames)

    numeric_features = [
        "avg_rating",
        "weighted_rating",
        "num_votes",
        "genres_count",
        "release_year",
        "total_clicks",
        "recommendation_clicks",
        "search_count",
        "views_count",
        "trending_score",
        "recent_views",
        "recent_ratings",
        "recent_avg_rating",
    ]
    categorical_features = ["primary_genre"]

    for feature in numeric_features:
        if feature not in dataset.columns:
            dataset[feature] = np.nan

    if "primary_genre" not in dataset.columns:
        dataset["primary_genre"] = "Unknown"

    dataset = dataset.dropna(subset=["movie_id", "user_id", "rating"]).reset_index(drop=True)
    dataset = _sanitize_numeric_features(dataset, numeric_features)

    return FeatureSet(
        dataframe=dataset,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
    )


def build_inference_features(movie_ids=None) -> pd.DataFrame:
    feature_df = get_candidate_movie_features(movie_ids=movie_ids)
    if feature_df.empty:
        return feature_df

    feature_df["trending_score"] = (
        0.7 * normalize_series(feature_df["recent_views"].fillna(0))
        + 0.3 * feature_df["recent_avg_rating"].fillna(0).clip(lower=0, upper=5) / 5.0
    )
    feature_df["primary_genre"] = feature_df["primary_genre"].fillna("Unknown")
    feature_df = _sanitize_numeric_features(
        feature_df,
        [
            "avg_rating",
            "weighted_rating",
            "num_votes",
            "genres_count",
            "release_year",
            "total_clicks",
            "recommendation_clicks",
            "search_count",
            "views_count",
            "trending_score",
            "recent_views",
            "recent_ratings",
            "recent_avg_rating",
        ],
    )
    return feature_df
