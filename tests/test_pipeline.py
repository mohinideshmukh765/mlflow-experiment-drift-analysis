"""
Unit and Integration Tests for MLflow Experiment Tracking & Drift Pipeline
Student: Aditi Rewadkar | Roll No: DS75 | PRN: 2425010132
"""

import pytest
import numpy as np
import pandas as pd
from src.data_loader import load_iris_data, generate_drift_datasets
from src.drift_detection import detect_data_drift
from src.train_model import train_and_evaluate_model


def test_load_iris_data():
    X_train, X_test, y_train, y_test, feature_names, target_names, df = load_iris_data(test_size=0.2, random_state=42)
    assert len(df) == 150
    assert len(X_train) == 120
    assert len(X_test) == 30
    assert len(feature_names) == 4
    assert len(target_names) == 3
    assert "petal length (cm)" in feature_names


def test_generate_drift_datasets():
    _, _, _, _, feature_names, _, df = load_iris_data()
    features_df = df[feature_names]
    ref_df, curr_df = generate_drift_datasets(
        features_df,
        shift_feature="petal length (cm)",
        shift_value=1.8,
        sample_ratio=0.5,
        random_state=42
    )
    assert len(ref_df) == 75
    assert len(curr_df) == 75
    
    # Check that petal length is shifted by exactly 1.8
    diff = curr_df["petal length (cm)"] - ref_df["petal length (cm)"]
    assert np.allclose(diff, 1.8)
    
    # Check that other features have 0 difference
    for f in ["sepal length (cm)", "sepal width (cm)", "petal width (cm)"]:
        assert np.allclose(curr_df[f], ref_df[f])


def test_drift_detection():
    _, _, _, _, feature_names, _, df = load_iris_data()
    features_df = df[feature_names]
    ref_df, curr_df = generate_drift_datasets(
        features_df,
        shift_feature="petal length (cm)",
        shift_value=1.8,
        sample_ratio=0.5,
        random_state=42
    )
    drift_df, summary = detect_data_drift(ref_df, curr_df, alpha=0.05)
    
    assert summary["drifted_features_count"] == 1
    assert summary["drifted_features"] == ["petal length (cm)"]
    assert summary["overall_status"] == "DRIFT_DETECTED"
    
    petal_row = drift_df[drift_df["feature"] == "petal length (cm)"].iloc[0]
    assert petal_row["drift_detected"] == True
    assert petal_row["p_value"] < 0.05
    assert petal_row["ks_statistic"] > 0.4
    
    sepal_row = drift_df[drift_df["feature"] == "sepal length (cm)"].iloc[0]
    assert sepal_row["drift_detected"] == False
    assert sepal_row["p_value"] > 0.95


def test_model_training(tmp_path):
    X_train, X_test, y_train, y_test, _, target_names, _ = load_iris_data(test_size=0.2, random_state=42)
    model, metrics, report, cm, fig_paths = train_and_evaluate_model(
        X_train, X_test, y_train, y_test,
        target_names=target_names,
        n_estimators=50,
        max_depth=4,
        random_state=42,
        output_dir=str(tmp_path)
    )
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_weighted"] >= 0.85
    assert cm.shape == (3, 3)
    assert len(fig_paths) == 2
