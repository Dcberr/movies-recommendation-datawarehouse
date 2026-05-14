from datetime import datetime
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "movie_analytics_mpl_cache"),
)

import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

try:
    from xgboost import XGBClassifier
except Exception as error:
    XGBClassifier = None
    XGBOOST_IMPORT_ERROR = error
else:
    XGBOOST_IMPORT_ERROR = None

from services.ai.ml.evaluator import (
    comparison_table,
    evaluate_binary_classifier,
    save_confusion_matrix_figure,
    save_feature_importance_figure,
    select_best_model,
)
from services.ai.ml.feature_engineering import build_training_dataset
from services.ai.ml.utils import RANDOM_STATE, TARGET_COLUMN, ensure_model_dir, save_artifact


def build_preprocessor(numeric_features, categorical_features):
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )


def build_estimators():
    estimators = {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=RANDOM_STATE,
            C=0.5,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=2,
            min_samples_split=4,
            class_weight="balanced_subsample",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }

    if XGBClassifier is not None:
        estimators["xgboost"] = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=RANDOM_STATE,
            n_jobs=4,
        )

    return estimators


def train_models(test_size: float = 0.2) -> dict:
    if XGBClassifier is None:
        raise ImportError(
            "xgboost is required to train the full model suite."
        ) from XGBOOST_IMPORT_ERROR

    feature_set = build_training_dataset()
    dataset = feature_set.dataframe
    if dataset.empty:
        raise ValueError("Training dataset is empty. Ensure the Azure SQL warehouse contains rating data.")

    X = dataset[feature_set.numeric_features + feature_set.categorical_features].copy()
    y = dataset[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    preprocessor = build_preprocessor(feature_set.numeric_features, feature_set.categorical_features)
    estimators = build_estimators()
    results = []
    bundles = {}

    ensure_model_dir()

    for model_name, estimator in estimators.items():
        fitted_preprocessor = clone(preprocessor)
        X_train_transformed = fitted_preprocessor.fit_transform(X_train)
        X_test_transformed = fitted_preprocessor.transform(X_test)

        fitted_model = clone(estimator)
        fitted_model.fit(X_train_transformed, y_train)

        y_pred = fitted_model.predict(X_test_transformed)
        y_proba = fitted_model.predict_proba(X_test_transformed)[:, 1]

        evaluation = evaluate_binary_classifier(model_name, y_test, y_pred, y_proba)
        transformed_feature_names = fitted_preprocessor.get_feature_names_out().tolist()

        feature_importance_path = None
        if hasattr(fitted_model, "feature_importances_"):
            feature_importance_path = save_feature_importance_figure(
                model_name,
                fitted_model.feature_importances_,
                transformed_feature_names,
            )

        confusion_matrix_path = save_confusion_matrix_figure(
            model_name,
            evaluation["confusion_matrix"],
        )

        bundle = {
            "model_name": model_name,
            "model": fitted_model,
            "preprocessor": fitted_preprocessor,
            "feature_names": transformed_feature_names,
            "numeric_features": feature_set.numeric_features,
            "categorical_features": feature_set.categorical_features,
            "metrics": {
                "accuracy": evaluation["accuracy"],
                "precision": evaluation["precision"],
                "recall": evaluation["recall"],
                "f1": evaluation["f1"],
                "roc_auc": evaluation["roc_auc"],
            },
            "classification_report": evaluation["classification_report"],
            "confusion_matrix": evaluation["confusion_matrix"],
            "feature_importance_path": str(feature_importance_path) if feature_importance_path else None,
            "confusion_matrix_path": str(confusion_matrix_path),
            "trained_at": datetime.utcnow().isoformat(),
        }

        save_artifact(bundle, model_name)
        bundles[model_name] = bundle
        results.append(evaluation)

    comparison_df = comparison_table(results)
    comparison_path = ensure_model_dir() / "model_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)

    best_model = select_best_model(results)
    summary = {
        "results": results,
        "comparison_table": comparison_df,
        "best_model": best_model["model"],
        "comparison_path": str(comparison_path),
        "artifacts": bundles,
    }
    return summary


if __name__ == "__main__":
    training_summary = train_models()
    print(training_summary["comparison_table"].to_string(index=False))
    print(f"Best model: {training_summary['best_model']}")
