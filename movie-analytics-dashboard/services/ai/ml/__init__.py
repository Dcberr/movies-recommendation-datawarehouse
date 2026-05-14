from services.ai.ml.predictor import get_best_model_info, predict_user_like_probability, score_candidate_movies


def train_models(*args, **kwargs):
    from services.ai.ml.trainer import train_models as _train_models
    return _train_models(*args, **kwargs)

__all__ = [
    "get_best_model_info",
    "predict_user_like_probability",
    "score_candidate_movies",
    "train_models",
]
