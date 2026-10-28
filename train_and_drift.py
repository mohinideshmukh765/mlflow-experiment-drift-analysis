"""
Main Pipeline Orchestrator: MLflow Experiment Tracking & Data Drift Analysis
Author: Aditi Rewadkar | Roll No: DS75 | PRN: 2425010132
Academic Year: A.Y. 2026-27 | Department: B.Tech CSE (Data Science)
"""

import os
import sys
import json
import mlflow
import mlflow.sklearn
import pandas as pd

from src.data_loader import load_iris_data, generate_drift_datasets
from src.train_model import train_and_evaluate_model
from src.drift_detection import detect_data_drift, plot_distribution_drift, plot_ks_metrics


def main():
    print("=" * 70)
    print("  MLFLOW EXPERIMENT TRACKING & DATA DRIFT PIPELINE")
    print("  Student: Aditi Rewadkar | Roll No: DS75 | PRN: 2425010132")
    print("  Department: B.Tech CSE (Data Science) | A.Y. 2026-27")
    print("=" * 70)
    
    # 0. Setup directories
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Configure MLflow local tracking
    tracking_uri = "file:./mlruns"
    mlflow.set_tracking_uri(tracking_uri)
    experiment_name = "Iris_MLflow_Drift_Analysis"
    mlflow.set_experiment(experiment_name)
    print(f"\n[+] Configured MLflow Tracking URI: {tracking_uri}")
    print(f"[+] Active MLflow Experiment: '{experiment_name}'")
    
    common_tags = {
        "student_name": "Aditi Rewadkar",
        "roll_number": "DS75",
        "prn": "2425010132",
        "department": "B.Tech CSE (Data Science)",
        "academic_year": "A.Y. 2026-27",
        "course": "MLOps / ISE-2 Theory & Practical",
        "framework": "Scikit-Learn & MLflow 3.12.0"
    }
    
    # ----------------------------------------------------
    # STEP 1: DATA INGESTION & MODEL TRAINING (RUN 1)
    # ----------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 1: Executing Run 1 -> Model_Training_And_Evaluation")
    print("-" * 70)
    
    X_train, X_test, y_train, y_test, feature_names, target_names, full_df = load_iris_data(
        test_size=0.20,
        random_state=42
    )
    print(f"Loaded Iris Dataset: {len(full_df)} total instances.")
    print(f"Features: {feature_names}")
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    n_estimators = 100
    max_depth = 5
    model_random_state = 29
    
    with mlflow.start_run(run_name="Model_Training_And_Evaluation") as run_model:
        model_run_id = run_model.info.run_id
        print(f"[+] Started Run ID: {model_run_id}")
        
        # Set tags
        mlflow.set_tags({**common_tags, "run_type": "model_training"})
        
        # Log parameters
        mlflow.log_params({
            "model_type": "RandomForestClassifier",
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": model_random_state,
            "test_size": 0.20,
            "total_samples": len(full_df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "num_features": len(feature_names),
            "num_classes": len(target_names)
        })
        
        # Train and evaluate
        model, metrics, class_report_str, cm, fig_paths = train_and_evaluate_model(
            X_train, X_test, y_train, y_test,
            target_names=target_names,
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=model_random_state,
            output_dir="artifacts"
        )
        
        # Log metrics
        mlflow.log_metrics({
            "accuracy": metrics["accuracy"],
            "precision_weighted": metrics["precision_weighted"],
            "recall_weighted": metrics["recall_weighted"],
            "f1_score": metrics["f1_weighted"],
            "precision_macro": metrics["precision_macro"],
            "recall_macro": metrics["recall_macro"],
            "f1_macro": metrics["f1_macro"]
        })
        
        # Save and log classification report
        report_path = os.path.join("reports", "classification_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=== Model Classification Report ===\n")
            f.write(f"Student: Aditi Rewadkar | Roll No: DS75 | PRN: 2425010132\n")
            f.write(f"Model: RandomForestClassifier (n_estimators={n_estimators}, max_depth={max_depth})\n\n")
            f.write(class_report_str)
        mlflow.log_artifact(report_path, artifact_path="reports")
        
        # Log visual figures
        for fig_p in fig_paths:
            mlflow.log_artifact(fig_p, artifact_path="plots")
            
        # Log serialized model
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="random_forest_model"
        )
        
        print("\nModel Evaluation Results:")
        print(f"  * Accuracy:           {metrics['accuracy']:.4f}")
        print(f"  * Weighted Precision: {metrics['precision_weighted']:.4f}")
        print(f"  * Weighted Recall:    {metrics['recall_weighted']:.4f}")
        print(f"  * Weighted F1-Score:  {metrics['f1_weighted']:.4f}")
        print(f"[+] Model and artifacts logged to MLflow Run: {model_run_id}")
        
    # ----------------------------------------------------
    # STEP 2: DATA DRIFT DETECTION & EVALUATION (RUN 2)
    # ----------------------------------------------------
    print("\n" + "-" * 70)
    print("STEP 2: Executing Run 2 -> Data_Drift_Analysis")
    print("-" * 70)
    
    # Features dataframe
    df_features = full_df[feature_names]
    shift_feature = "petal length (cm)"
    shift_val = 1.8
    alpha = 0.05
    
    reference_df, current_df = generate_drift_datasets(
        df_features=df_features,
        shift_feature=shift_feature,
        shift_value=shift_val,
        sample_ratio=0.50,
        random_state=42
    )
    print(f"Reference dataset shape: {reference_df.shape} (unperturbed baseline)")
    print(f"Current dataset shape:   {current_df.shape} (injected shift: +{shift_val}cm on '{shift_feature}')")
    
    with mlflow.start_run(run_name="Data_Drift_Analysis") as run_drift:
        drift_run_id = run_drift.info.run_id
        print(f"[+] Started Run ID: {drift_run_id}")
        
        mlflow.set_tags({**common_tags, "run_type": "drift_monitoring"})
        
        # Log drift experiment parameters
        mlflow.log_params({
            "statistical_test": "Kolmogorov-Smirnov (2-sample)",
            "significance_threshold_alpha": alpha,
            "drift_type": "Covariate Shift (Data Drift)",
            "simulation_offset_feature": shift_feature,
            "simulation_offset_val": shift_val,
            "reference_samples": len(reference_df),
            "current_samples": len(current_df)
        })
        
        # Perform KS test
        drift_results_df, drift_summary = detect_data_drift(reference_df, current_df, alpha=alpha)
        
        # Log KS statistics and p-values as MLflow metrics
        for _, row in drift_results_df.iterrows():
            sanitized_name = row["feature"].replace(" ", "_").replace("(", "").replace(")", "")
            mlflow.log_metric(f"ks_stat_{sanitized_name}", row["ks_statistic"])
            mlflow.log_metric(f"p_val_{sanitized_name}", row["p_value"])
            
        mlflow.log_metric("total_drifted_features", drift_summary["drifted_features_count"])
        
        # Save CSV report
        csv_path = os.path.join("reports", "drift_results.csv")
        drift_results_df.to_csv(csv_path, index=False)
        mlflow.log_artifact(csv_path, artifact_path="drift_reports")
        
        # Save JSON summary
        json_path = os.path.join("reports", "drift_summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(drift_summary, f, indent=4)
        mlflow.log_artifact(json_path, artifact_path="drift_reports")
        
        # Generate diagnostic plots
        dist_plot_path = plot_distribution_drift(reference_df, current_df, drift_results_df, "artifacts/drift_distribution.png")
        ks_plot_path = plot_ks_metrics(drift_results_df, "artifacts/feature_drift.png")
        
        mlflow.log_artifact(dist_plot_path, artifact_path="drift_plots")
        mlflow.log_artifact(ks_plot_path, artifact_path="drift_plots")
        
        print("\nData Drift Analysis Results (Kolmogorov-Smirnov Test):")
        print(drift_results_df[["feature", "ks_statistic", "p_value", "null_hypothesis", "drift_status"]].to_string(index=False))
        print(f"\nOverall Pipeline Drift Status: {drift_summary['overall_status']}")
        print(f"Drifted Features Detected:    {drift_summary['drifted_features']}")
        print(f"[+] Drift reports and visualizations logged to MLflow Run: {drift_run_id}")
        
    print("\n" + "=" * 70)
    print("  ALL EXPERIMENT RUNS COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
