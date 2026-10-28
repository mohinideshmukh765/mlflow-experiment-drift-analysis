"""
Data Ingestion and Drift Simulation Module
Provides reproducible dataset loading and synthetic covariate shift generation.
"""

import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_iris_data(test_size=0.2, random_state=42):
    """
    Load the Scikit-Learn Iris dataset and perform stratified train/test split.
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, feature_names, target_names, full_df)
    """
    iris = load_iris()
    feature_names = [name for name in iris.feature_names]
    target_names = list(iris.target_names)
    
    df = pd.DataFrame(iris.data, columns=feature_names)
    df['target'] = iris.target
    
    X = df[feature_names]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    return X_train, X_test, y_train, y_test, feature_names, target_names, df


def generate_drift_datasets(df_features, shift_feature="petal length (cm)", shift_value=1.8, sample_ratio=0.5, random_state=42):
    """
    Generate baseline reference and drifted current datasets.
    
    Args:
        df_features (pd.DataFrame): Input feature DataFrame.
        shift_feature (str): Feature to inject synthetic drift into.
        shift_value (float): Controlled additive offset.
        sample_ratio (float): Fraction of dataset for reference sample.
        random_state (int): Reproducibility seed.
        
    Returns:
        tuple: (reference_df, current_df)
    """
    # Baseline reference dataset: 50% random reproducible sample
    reference_df = df_features.sample(frac=sample_ratio, random_state=random_state).copy().reset_index(drop=True)
    
    # Current dataset: duplicate baseline with controlled shift injected into target feature
    current_df = reference_df.copy()
    if shift_feature in current_df.columns:
        current_df[shift_feature] = current_df[shift_feature] + shift_value
    else:
        raise ValueError(f"Feature '{shift_feature}' not found in dataset columns: {list(current_df.columns)}")
        
    return reference_df, current_df
