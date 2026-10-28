"""
Statistical Data Drift Detection Module
Implements Two-Sample Kolmogorov-Smirnov (KS) test and diagnostic visualization.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp


def detect_data_drift(reference_df, current_df, alpha=0.05):
    """
    Perform Two-Sample Kolmogorov-Smirnov (KS) test across all numerical features.
    
    Args:
        reference_df (pd.DataFrame): Baseline reference dataset.
        current_df (pd.DataFrame): Current monitored dataset.
        alpha (float): Significance threshold (default: 0.05).
        
    Returns:
        tuple: (drift_results_df, summary_dict)
    """
    results = []
    
    for feature in reference_df.columns:
        ref_values = reference_df[feature].dropna().values
        curr_values = current_df[feature].dropna().values
        
        ks_res = ks_2samp(ref_values, curr_values)
        ks_stat = float(ks_res.statistic)
        p_val = float(ks_res.pvalue)
        
        drift_detected = bool(p_val < alpha)
        drift_status = "Drift Detected" if drift_detected else "No Drift"
        null_hyp = "Reject H0" if drift_detected else "Fail to Reject"
        
        results.append({
            "feature": feature,
            "ks_statistic": round(ks_stat, 5),
            "p_value": round(p_val, 6),
            "alpha_threshold": alpha,
            "null_hypothesis": null_hyp,
            "drift_detected": drift_detected,
            "drift_status": drift_status
        })
        
    drift_df = pd.DataFrame(results)
    
    drifted_count = int(drift_df["drift_detected"].sum())
    total_features = len(drift_df)
    overall_status = "DRIFT_DETECTED" if drifted_count > 0 else "NO_DRIFT"
    
    summary_dict = {
        "total_features": total_features,
        "drifted_features_count": drifted_count,
        "drifted_features": drift_df[drift_df["drift_detected"]]["feature"].tolist(),
        "overall_status": overall_status,
        "significance_threshold_alpha": alpha,
        "statistical_test": "Two-Sample Kolmogorov-Smirnov (KS) test"
    }
    
    return drift_df, summary_dict


def plot_distribution_drift(reference_df, current_df, drift_results_df, output_path="artifacts/drift_distribution.png"):
    """
    Generate 2x2 comparison histograms for reference vs current datasets.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    features = list(reference_df.columns)
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), dpi=150)
    axes = axes.flatten()
    
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    for idx, feature in enumerate(features):
        ax = axes[idx]
        ref_vals = reference_df[feature].values
        curr_vals = current_df[feature].values
        
        # Get drift metrics for feature
        f_row = drift_results_df[drift_results_df["feature"] == feature].iloc[0]
        stat = f_row["ks_statistic"]
        pval = f_row["p_value"]
        drift = f_row["drift_detected"]
        
        # Plot histograms
        bins = np.linspace(min(ref_vals.min(), curr_vals.min()), max(ref_vals.max(), curr_vals.max()), 16)
        ax.hist(ref_vals, bins=bins, density=True, alpha=0.55, color="#1f77b4", label="Reference Data", edgecolor="#0b456e")
        ax.hist(curr_vals, bins=bins, density=True, alpha=0.55, color="#d62728", label="Current (Shifted) Data", edgecolor="#871213")
        
        # Title and labels
        ax.set_title(f"{feature}\nKS Stat = {stat:.4f} | p-value = {pval:.4e}", fontsize=11, fontweight="bold", pad=8)
        ax.set_xlabel("Feature Value", fontsize=10)
        ax.set_ylabel("Probability Density", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
        
        # Drift badge
        badge_text = "DRIFT DETECTED" if drift else "NO DRIFT"
        badge_color = "#c0392b" if drift else "#27ae60"
        ax.text(
            0.04, 0.92, badge_text,
            transform=ax.transAxes,
            fontsize=9.5,
            fontweight="bold",
            color=badge_color,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=badge_color, lw=1.5)
        )
        
    fig.suptitle("Iris Feature Distribution Comparison (Reference vs. Current)", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path


def plot_ks_metrics(drift_results_df, output_path="artifacts/feature_drift.png"):
    """
    Generate horizontal bar charts showing KS statistics and p-values per feature.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)
    
    # Sort order
    sorted_df = drift_results_df.copy().iloc[::-1].reset_index(drop=True)
    features = sorted_df["feature"].tolist()
    ks_stats = sorted_df["ks_statistic"].tolist()
    p_values = sorted_df["p_value"].tolist()
    drift_flags = sorted_df["drift_detected"].tolist()
    
    # 1. Left Plot: KS Statistics
    colors_ks = ["#d62728" if d else "#4575b4" for d in drift_flags]
    bars1 = ax1.barh(features, ks_stats, color=colors_ks, height=0.45, edgecolor="black")
    ax1.set_xlim(0, 1.0)
    ax1.set_xlabel("Kolmogorov-Smirnov Statistic (D)", fontsize=11, fontweight="bold")
    ax1.set_title("KS Test Statistic per Feature (Higher = Greater Shift)", fontsize=12, fontweight="bold", pad=10)
    ax1.grid(axis="x", linestyle="--", alpha=0.6)
    
    for bar in bars1:
        w = bar.get_width()
        ax1.text(w + 0.02, bar.get_y() + bar.get_height() / 2.0, f"{w:.4f}", va="center", fontsize=9.5, fontweight="bold")
        
    # 2. Right Plot: p-values
    colors_p = ["#d62728" if d else "#2ca02c" for d in drift_flags]
    bars2 = ax2.barh(features, p_values, color=colors_p, height=0.45, edgecolor="black")
    ax2.set_xlim(0, 1.05)
    ax2.axvline(0.05, color="red", linestyle="--", linewidth=1.8, label=r"Threshold $\alpha = 0.05$")
    ax2.set_xlabel("p-value", fontsize=11, fontweight="bold")
    ax2.set_title("Statistical Significance p-value (p < 0.05 => Drift)", fontsize=12, fontweight="bold", pad=10)
    ax2.grid(axis="x", linestyle="--", alpha=0.6)
    ax2.legend(loc="lower right", fontsize=10, framealpha=0.9)
    
    for bar in bars2:
        w = bar.get_width()
        text_x = min(w + 0.02, 0.92)
        ax2.text(text_x, bar.get_y() + bar.get_height() / 2.0, f"{w:.4f}", va="center", fontsize=9.5, fontweight="bold")
        
    fig.suptitle("Statistical Data Drift Evaluation Metrics", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    return output_path
