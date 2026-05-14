from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    ConfusionMatrixDisplay,
)

from services.ai.ml.utils import MODEL_DIR, MODEL_METRIC, ensure_model_dir


def evaluate_binary_classifier(model_name, y_true, y_pred, y_proba) -> dict:
    metrics = {
        "model": model_name,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_proba),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred),
    }
    return metrics


def comparison_table(results: list) -> pd.DataFrame:
    if not results:
        return pd.DataFrame(columns=["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"])

    rows = []
    for result in results:
        rows.append(
            {
                "Model": result["model"],
                "Accuracy": result["accuracy"],
                "Precision": result["precision"],
                "Recall": result["recall"],
                "F1": result["f1"],
                "ROC-AUC": result["roc_auc"],
            }
        )

    return pd.DataFrame(rows).sort_values("ROC-AUC", ascending=False).reset_index(drop=True)


def select_best_model(results: list, metric: str = MODEL_METRIC) -> dict:
    if not results:
        raise ValueError("No evaluation results available to choose a best model.")
    return max(results, key=lambda result: result[metric])


def save_confusion_matrix_figure(model_name: str, matrix, labels=None) -> Path:
    ensure_model_dir()
    labels = labels or ["Dislike", "Like"]
    figure, axis = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=labels).plot(
        ax=axis,
        cmap="Blues",
        colorbar=False,
    )
    axis.set_title(f"{model_name} Confusion Matrix")
    output_path = MODEL_DIR / f"{model_name}_confusion_matrix.png"
    figure.tight_layout()
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return output_path


def save_feature_importance_figure(model_name: str, importances, feature_names, top_k: int = 15) -> Path:
    ensure_model_dir()
    importance_frame = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(top_k)
    )

    figure, axis = plt.subplots(figsize=(8, 5))
    axis.barh(importance_frame["feature"][::-1], importance_frame["importance"][::-1], color="#4f81bd")
    axis.set_title(f"{model_name} Feature Importance")
    axis.set_xlabel("Importance")
    figure.tight_layout()

    output_path = MODEL_DIR / f"{model_name}_feature_importance.png"
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return output_path
