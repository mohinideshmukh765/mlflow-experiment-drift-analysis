# MLflow Installation, Experiment Tracking and Data Drift Analysis

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![MLflow](https://img.shields.io/badge/MLflow-3.12.0-orange.svg)](https://mlflow.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.8.0-green.svg)](https://scikit-learn.org/)
[![Pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An end-to-end, reproducible **MLOps In-Semester Evaluation (ISE-2)** practical project demonstrating:
- Local Python virtual environment configuration and MLflow setup on Windows 11.
- Machine learning experiment tracking (parameters, metrics, tags, models, and artifacts) using MLflow.
- Multiclass classification model training using Random Forest on the Scikit-Learn Iris dataset.
- Continuous statistical data drift detection using the two-sample Kolmogorov–Smirnov (KS) test from `scipy.stats`.
- Automated generation of drift audit reports (CSV, JSON) and diagnostic visualizations (PNG).
- Complete automated unit and integration test suite using `pytest`.

---

## Student Details

| Attribute | Details |
| :--- | :--- |
| **Student Name** | Aditi Rewadkar |
| **PRN / Roll Number** | 2425010132 (Roll No: DS75) |
| **Department / Class** | Department of CSE (Data Science) / Final Year B.Tech CSE (DS), Semester VII |
| **Academic Year** | A.Y. 2026-27 |
| **Institution** | Kolhapur Institute of Technology's College of Engineering (Autonomous), Kolhapur |
| **Course** | MLOps & Machine Learning Engineering / ISE-2 |
| **GitHub Repository** | [https://github.com/mohinideshmukh765/mlflow-experiment-drift-analysis](https://github.com/mohinideshmukh765/mlflow-experiment-drift-analysis) |

---

## 1. Project Overview & Architecture

Modern machine learning models degrade in production when real-world data distributions deviate from training data (known as **Covariate Shift** or **Data Drift**). This project implements an automated MLOps pipeline that tracks model training runs and establishes statistical guardrails to alert engineers when features drift significantly.

```
+-------------------------------------------------------------------------------+
|                         MLOps Pipeline Architecture                           |
+-------------------------------------------------------------------------------+
|
+------------------------+------------------------+
|                                                 |
v                                                 v
[ 1. Data Ingestion & Split ]           [ 4. Data Drift Simulation ]
- Scikit-Learn Iris Dataset             - Baseline Reference Data (50%, 75 rows)
- 150 instances, 4 features             - Shifted Current Data (+1.8cm Petal)
- Stratified 80/20 Train/Test Split                       |
|                                                         v
v                                               [ 5. Two-Sample KS Test ]
[ 2. Random Forest Classifier ]                 - Null Hypothesis: Distributions Equal
- n_estimators = 100, max_depth = 5             - Significance threshold: alpha = 0.05
- Evaluation: Acc, Prec, Rec, F1                - Computes KS Statistic & p-values
|                                                         |
v                                                         v
[ 3. MLflow Tracking Run 1 ]                    [ 6. MLflow Tracking Run 2 ]
- Log Hyperparameters & Student Tags            - Log KS Statistics & p-values
- Log Evaluation Metrics                        - Log CSV/JSON Drift Reports
- Log Trained Sklearn Model                     - Log Distribution Comparison Plots
|                                                         |
+------------------------+------------------------+
|
v
+---------------------------------+
|   MLflow Local Tracking Store   |
|   - Experiment: Iris_..._Drift  |
|   - Web Dashboard: :5001        |
+---------------------------------+
```

---

## 2. Directory Structure

```text
MLFlowDataAnalysis/
├── artifacts/                           # Diagnostic plots and visual artifacts
│   ├── drift_distribution.png           # 2x2 Feature distribution comparison
│   ├── feature_drift.png                # KS test statistics & p-values bar chart
│   ├── model_confusion_matrix.png       # Random Forest confusion matrix heatmap
│   └── model_metrics.png                # Evaluation metrics summary bar chart
├── mlruns/                              # MLflow tracking backend database & store
├── reports/                             # Generated audit reports
│   ├── classification_report.txt        # Full scikit-learn precision/recall report
│   ├── drift_results.csv                # Tabular feature-level drift metrics
│   └── drift_summary.json               # Structured drift pipeline audit payload
├── screenshots/                         # Verification screenshots
│   ├── 01_mlflow_training_runs.png      # MLflow experiments dashboard
│   ├── 02_model_training_run.png        # Run 1 Model Training & Evaluation details
│   ├── 02b_model_training_artifacts.png # Run 1 Artifacts tab
│   ├── 03_data_drift_run.png            # Run 2 Data Drift Analysis details
│   ├── 03b_data_drift_artifacts.png     # Run 2 Artifacts tab
│   ├── 04_terminal_execution.png        # PowerShell execution & pytest verification
│   ├── 05_project_tree_explorer.png     # Project workspace tree
│   ├── 06_drift_results_csv_view.png    # Drift results CSV artifact
│   └── 07_classification_report_view.png# Classification report artifact
├── src/                                 # Modular Python source package
│   ├── __init__.py                      # Package descriptor
│   ├── data_loader.py                   # Ingestion & reproducible drift simulation
│   ├── drift_detection.py               # Two-sample KS test & visualization
│   └── train_model.py                   # Random Forest training & evaluation
├── tests/                               # Automated unit & integration tests
│   └── test_pipeline.py                 # Pytest suite
├── .gitignore                           # Git excluded patterns
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Pinned project dependencies
├── Theory-ISE2-MLFlow Data Analysis.docx# Assignment template & final report
└── train_and_drift.py                   # Main pipeline orchestrator script
```

---

## 3. Environment Setup & Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/mohinideshmukh765/mlflow-experiment-drift-analysis.git
cd mlflow-experiment-drift-analysis
```

### Step 2: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

---

## 4. Execution & Pipeline Tracking

### Run Full Pipeline
To execute data ingestion, Random Forest training, MLflow tracking, and statistical drift detection:
```bash
python train_and_drift.py
```

### Run Automated Test Suite
```bash
python -m pytest
```

### Launch MLflow Web UI
To inspect the visual tracking dashboard, run comparisons, and download artifacts:
```bash
mlflow ui --port 5001
```
Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## 5. Statistical Data Drift Results

### Kolmogorov–Smirnov (KS) Test Summary ($\alpha = 0.05$)

| Feature Name | KS Statistic ($D$) | p-value | Threshold ($\alpha$) | Null Hypothesis ($H_0$) | Drift Decision |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `sepal length (cm)` | 0.00000 | 1.0000 | 0.05 | Fail to Reject | **No Drift** |
| `sepal width (cm)` | 0.00000 | 1.0000 | 0.05 | Fail to Reject | **No Drift** |
| `petal length (cm)` | **0.45333** | **0.0000** | 0.05 | **Reject $H_0$** | <span style="color:red">**Drift Detected**</span> |
| `petal width (cm)` | 0.00000 | 1.0000 | 0.05 | Fail to Reject | **No Drift** |

**Overall Pipeline Status:** `DRIFT_DETECTED` (1 of 4 features drifted).

---

## 6. Model Evaluation Results

- **Model Architecture:** Random Forest Classifier (`n_estimators=100`, `max_depth=5`, `random_state=29`)
- **Accuracy:** `0.9000` (90.00%)
- **Weighted Precision:** `0.9024`
- **Weighted Recall:** `0.9000`
- **Weighted F1-Score:** `0.8997`

---

## 7. License
This project is open-source under the MIT License.
