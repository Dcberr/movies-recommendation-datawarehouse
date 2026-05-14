import numpy as np
import pandas as pd

from services.ai.ml.feature_engineering import build_inference_features
from services.ai.ml.utils import (
    MODEL_METRIC,
    available_model_paths,
    confidence_from_probability,
    load_artifact,
    to_dataframe,
)


def get_available_model_bundles() -> dict:
    model_paths = available_model_paths()
    return {
        model_name: load_artifact(model_name)
        for model_name in model_paths
    }


def get_best_model_bundle(metric: str = MODEL_METRIC):
    bundles = get_available_model_bundles()
    if not bundles:
        raise FileNotFoundError("No trained ML models were found in services/ai/models.")

    return max(
        bundles.values(),
        key=lambda bundle: bundle.get("metrics", {}).get(metric, float("-inf")),
    )


def get_best_model_info(metric: str = MODEL_METRIC) -> dict:
    bundle = get_best_model_bundle(metric=metric)
    return {
        "model_name": bundle["model_name"],
        "metrics": bundle.get("metrics", {}),
        "trained_at": bundle.get("trained_at"),
    }


def _prepare_prediction_frame(movie_features, bundle) -> pd.DataFrame:
    frame = to_dataframe(movie_features)
    required_columns = bundle["numeric_features"] + bundle["categorical_features"]

    for column in required_columns:
        if column not in frame.columns:
            frame[column] = np.nan if column in bundle["numeric_features"] else "Unknown"

    return frame[required_columns].copy()


def predict_user_like_probability(movie_features, model_name: str = None) -> pd.DataFrame:
    bundle = load_artifact(model_name) if model_name else get_best_model_bundle()
    model = bundle["model"]
    preprocessor = bundle["preprocessor"]

    prediction_frame = _prepare_prediction_frame(movie_features, bundle)
    transformed_features = preprocessor.transform(prediction_frame)

    probabilities = model.predict_proba(transformed_features)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    confidence = confidence_from_probability(probabilities)

    result_df = to_dataframe(movie_features)
    result_df["ml_probability"] = probabilities
    result_df["ml_prediction"] = predictions
    result_df["ml_confidence"] = confidence
    result_df["best_model"] = bundle["model_name"]

    return result_df


def score_candidate_movies(candidate_df: pd.DataFrame, model_name: str = None):
    if candidate_df.empty:
        return candidate_df, None

    candidate_frame = candidate_df.copy()
    if "movie_id" not in candidate_frame.columns:
        raise ValueError("Candidate dataframe must include movie_id for ML scoring.")

    inference_features = build_inference_features(candidate_frame["movie_id"].dropna().astype(int).tolist())
    merged = candidate_frame.merge(inference_features, on="movie_id", how="left", suffixes=("", "_feature"))

    for preferred_column in ("title", "release_year", "avg_rating", "weighted_rating", "num_votes"):
        feature_column = f"{preferred_column}_feature"
        if feature_column in merged.columns and preferred_column in merged.columns:
            merged[preferred_column] = merged[preferred_column].fillna(merged[feature_column])
            merged = merged.drop(columns=[feature_column])
        elif feature_column in merged.columns:
            merged = merged.rename(columns={feature_column: preferred_column})

    scored = predict_user_like_probability(merged, model_name=model_name)
    model_info = {
        "model_name": scored["best_model"].iloc[0],
        "mean_probability": float(scored["ml_probability"].mean()),
    }
    return scored, model_info
