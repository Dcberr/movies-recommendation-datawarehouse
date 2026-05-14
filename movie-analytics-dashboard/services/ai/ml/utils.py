from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


RANDOM_STATE = 42
TARGET_COLUMN = "like"
MODEL_METRIC = "roc_auc"
MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_FILE_MAP = {
    "logistic_regression": MODEL_DIR / "logistic_regression.pkl",
    "random_forest": MODEL_DIR / "random_forest.pkl",
    "xgboost": MODEL_DIR / "xgboost.pkl",
}


def ensure_model_dir():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR


def to_dataframe(records) -> pd.DataFrame:
    if isinstance(records, pd.DataFrame):
        return records.copy()
    if isinstance(records, dict):
        return pd.DataFrame([records])
    return pd.DataFrame(records)


def normalize_series(series: pd.Series) -> pd.Series:
    if series.empty:
        return series

    clean_series = series.fillna(0.0).astype(float)
    min_value = clean_series.min()
    max_value = clean_series.max()

    if np.isclose(max_value, min_value):
        return pd.Series(np.full(len(clean_series), 0.5), index=clean_series.index)

    return (clean_series - min_value) / (max_value - min_value)


def confidence_from_probability(probability):
    probability = np.asarray(probability, dtype=float)
    return np.abs(probability - 0.5) * 2.0


def model_artifact_path(model_name: str) -> Path:
    ensure_model_dir()
    if model_name not in MODEL_FILE_MAP:
        raise ValueError(f"Unsupported model name: {model_name}")
    return MODEL_FILE_MAP[model_name]


def save_artifact(payload: dict, model_name: str) -> Path:
    payload = payload.copy()
    payload["saved_at"] = datetime.utcnow().isoformat()
    output_path = model_artifact_path(model_name)
    joblib.dump(payload, output_path)
    return output_path


def load_artifact(model_name: str):
    artifact_path = model_artifact_path(model_name)
    if not artifact_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {artifact_path}")
    return joblib.load(artifact_path)


def available_model_paths() -> dict:
    ensure_model_dir()
    return {
        model_name: path
        for model_name, path in MODEL_FILE_MAP.items()
        if path.exists()
    }
