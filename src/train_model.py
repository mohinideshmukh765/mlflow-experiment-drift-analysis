"""
Model Training and Evaluation Module
Trains a Random Forest multiclass classifier, computes metrics, and generates evaluation plots.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def train_and_evaluate_model(X_train, X_test, y_train, y_test, target_names, n_estimators=100, max_depth=5, random_state=42, output_dir="artifacts"):
    """
    Train Random Forest classifier, evaluate metrics, and save visual artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Initialize and train model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    model.fit(X_train, y_train)
    
    # 2. Inference
    y_pred = model.predict(X_test)
    
    # 3. Calculate metrics
    accuracy = float(accuracy_score(y_test, y_pred))
    precision_weighted = float(precision_score(y_test, y_pred, average="weighted"))
    recall_weighted = float(recall_score(y_test, y_pred, average="weighted"))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted"))
    precision_macro = float(precision_score(y_test, y_pred, average="macro"))
    recall_macro = float(recall_score(y_test, y_pred, average="macro"))
    f1_macro = float(f1_score(y_test, y_pred, average="macro"))
    
    cm = confusion_matrix(y_test, y_pred)
    class_report_str = classification_report(y_test, y_pred, target_names=target_names, digits=4)
    
    metrics = {
        "accuracy": round(accuracy, 4),
        "precision_weighted": round(precision_weighted, 4),
        "recall_weighted": round(recall_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4)
    }
    
    # 4. Generate Confusion Matrix Plot
    cm_path = os.path.join(output_dir, "model_confusion_matrix.png")
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    cax = ax.matshow(cm, cmap="Blues", alpha=0.8)
    fig.colorbar(cax)
    
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > cm.max() / 2 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=12, fontweight="bold")
            
    ax.set_xticks(range(len(target_names)))
    ax.set_yticks(range(len(target_names)))
    ax.set_xticklabels(target_names, fontsize=10)
    ax.set_yticklabels(target_names, fontsize=10)
    ax.set_xlabel("Predicted Species", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("True Species", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title("Random Forest Confusion Matrix", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(cm_path)
    plt.close()
    
    # 5. Generate Metrics Summary Bar Plot
    metrics_plot_path = os.path.join(output_dir, "model_metrics.png")
    metric_labels = ["Accuracy", "Weighted Precision", "Weighted Recall", "Weighted F1"]
    metric_values = [metrics["accuracy"], metrics["precision_weighted"], metrics["recall_weighted"], metrics["f1_weighted"]]
    
    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    bars = ax.bar(metric_labels, metric_values, color=["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"], width=0.55, edgecolor="black")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score", fontsize=11, fontweight="bold")
    ax.set_title("Random Forest Evaluation Metrics (Test Set)", fontsize=12, fontweight="bold", pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 0.02, f"{h:.4f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
        
    plt.tight_layout()
    plt.savefig(metrics_plot_path)
    plt.close()
    
    return model, metrics, class_report_str, cm, [cm_path, metrics_plot_path]
