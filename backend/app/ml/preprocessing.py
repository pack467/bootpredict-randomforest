"""
Data Preprocessing Module
=========================
Handles data loading, encoding, and train-test splitting for the 
Random Forest classifier.

Features:
- Label encoding for categorical features
- Encoder persistence (save/load with joblib)
- Stratified train-test split
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

from app.config import DATASET_CSV_PATH, ENCODERS_PATH


def load_dataset(csv_path=None):
    """
    Load the football boots dataset from CSV.
    
    Args:
        csv_path: Path to CSV file. Uses default if None.
    
    Returns:
        pandas.DataFrame: Loaded dataset
    
    Raises:
        FileNotFoundError: If dataset file doesn't exist
    """
    path = csv_path or DATASET_CSV_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")
    
    df = pd.read_csv(path)
    
    # Validate required columns
    required_columns = ["peminatan", "brand", "posisi", "label_sepatu"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Clean data - strip whitespace and lowercase
    for col in required_columns:
        df[col] = df[col].str.strip().str.lower()
    
    # Remove rows with null values
    df = df.dropna(subset=required_columns)
    
    return df


def create_encoders(df):
    """
    Create and fit LabelEncoders for all categorical features and target.
    
    Args:
        df: DataFrame with the dataset
    
    Returns:
        dict: Dictionary of fitted LabelEncoders keyed by column name
    """
    encoders = {}
    
    for col in ["peminatan", "brand", "posisi", "label_sepatu"]:
        le = LabelEncoder()
        le.fit(df[col])
        encoders[col] = le
    
    return encoders


def save_encoders(encoders, path=None):
    """
    Save fitted LabelEncoders to disk using joblib.
    
    Args:
        encoders: Dictionary of LabelEncoders
        path: Output path. Uses default if None.
    """
    save_path = path or ENCODERS_PATH
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(encoders, save_path)
    print(f"Encoders saved to: {save_path}")


def load_encoders(path=None):
    """
    Load previously saved LabelEncoders from disk.
    
    Args:
        path: Path to encoders file. Uses default if None.
    
    Returns:
        dict: Dictionary of LabelEncoders
    
    Raises:
        FileNotFoundError: If encoders file doesn't exist
    """
    load_path = path or ENCODERS_PATH
    if not os.path.exists(load_path):
        raise FileNotFoundError(f"Encoders not found at: {load_path}")
    
    return joblib.load(load_path)


def encode_features(df, encoders):
    """
    Encode categorical features using fitted LabelEncoders.
    
    Args:
        df: DataFrame with raw categorical features
        encoders: Dictionary of fitted LabelEncoders
    
    Returns:
        tuple: (X, y) where X is encoded features array and y is encoded target array
    """
    X = pd.DataFrame()
    
    # Encode feature columns
    for col in ["peminatan", "brand", "posisi"]:
        X[col] = encoders[col].transform(df[col])
    
    # Encode target column
    y = encoders["label_sepatu"].transform(df["label_sepatu"])
    
    return X.values, y


def encode_single_input(peminatan, brand, posisi, encoders):
    """
    Encode a single user input for prediction.
    
    Args:
        peminatan: Play style preference (e.g., "speed")
        brand: Preferred brand (e.g., "nike")
        posisi: Player position (e.g., "striker")
        encoders: Dictionary of fitted LabelEncoders
    
    Returns:
        numpy.ndarray: Encoded input as 2D array for prediction
    """
    encoded = np.array([
        encoders["peminatan"].transform([peminatan])[0],
        encoders["brand"].transform([brand])[0],
        encoders["posisi"].transform([posisi])[0]
    ]).reshape(1, -1)
    
    return encoded


def preprocess_pipeline(csv_path=None, test_size=0.2, random_state=42):
    """
    Complete preprocessing pipeline: load, encode, split.
    
    Args:
        csv_path: Path to CSV dataset
        test_size: Fraction of data for testing (default: 0.2)
        random_state: Random seed for reproducibility
    
    Returns:
        tuple: (X_train, X_test, y_train, y_test, encoders)
    """
    # Step 1: Load dataset
    df = load_dataset(csv_path)
    print(f"Loaded dataset: {len(df)} samples")
    print(f"Columns: {list(df.columns)}")
    print(f"Label distribution:\n{df['label_sepatu'].value_counts()}")
    
    # Step 2: Create and fit encoders
    encoders = create_encoders(df)
    
    # Step 3: Encode features
    X, y = encode_features(df, encoders)
    print(f"\nEncoded features shape: {X.shape}")
    print(f"Feature names: ['peminatan', 'brand', 'posisi']")
    
    # Step 4: Train-test split (stratified to maintain label distribution)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y
    )
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Step 5: Save encoders
    save_encoders(encoders)
    
    return X_train, X_test, y_train, y_test, encoders
