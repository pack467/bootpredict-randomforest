"""
Model Training Module
=====================
Handles training the Random Forest classifier, evaluating performance,
and saving the trained model.

Evaluation metrics:
- Accuracy
- Precision (weighted)
- Recall (weighted)
- F1-score (weighted)
- Confusion matrix
- Classification report
- Stratified K-Fold Cross-Validation
"""

import os
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
import joblib

from app.config import MODEL_PATH, DATASET_CSV_PATH
from app.ml.preprocessing import preprocess_pipeline, load_encoders


def train_model(csv_path=None, n_estimators=100, random_state=42):
    """
    Train a Random Forest classifier on the football boots dataset.

    This function performs the complete ML training workflow:
    1. Data preprocessing (via preprocessing pipeline)
    2. Model training with RandomForestClassifier
    3. Model evaluation with multiple metrics
    4. Stratified K-Fold Cross-Validation
    5. Model persistence (saved to disk)
    6. Cache invalidation for prediction module

    Args:
        csv_path: Path to training data CSV. Uses default if None.
        n_estimators: Number of trees in the random forest (default: 100)
        random_state: Random seed for reproducibility

    Returns:
        dict: Training results containing metrics and model info
    """
    print("=" * 60)
    print("FOOTBALL BOOTS CLASSIFICATION - MODEL TRAINING")
    print("=" * 60)

    # Step 1: Preprocess data
    print("\n[Step 1] Preprocessing data...")
    X_train, X_test, y_train, y_test, encoders = preprocess_pipeline(
        csv_path=csv_path,
        random_state=random_state
    )

    # Step 2: Initialize and train Random Forest
    print("\n[Step 2] Training Random Forest Classifier...")
    print(f"  - n_estimators: {n_estimators}")
    print(f"  - max_depth: 10")
    print(f"  - min_samples_split: 5")
    print(f"  - min_samples_leaf: 2")
    print(f"  - class_weight: balanced")
    print(f"  - random_state: {random_state}")

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        max_depth=10,             # Limit depth to prevent overfitting on small dataset
        min_samples_split=5,      # Require more samples before splitting
        min_samples_leaf=2,       # Require more samples in leaf nodes
        class_weight="balanced",  # Handle class imbalance
        n_jobs=-1                 # Use all CPU cores
    )

    model.fit(X_train, y_train)
    print("  Training complete!")

    # Step 3: Evaluate model on test set
    print("\n[Step 3] Evaluating model on test set...")
    y_pred = model.predict(X_test)

    # Get class names from encoder
    label_encoder = encoders["label_sepatu"]
    class_names = list(label_encoder.classes_)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall_val = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # Classification report (detailed per-class metrics)
    report = classification_report(
        y_test, y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    report_text = classification_report(
        y_test, y_pred,
        target_names=class_names,
        zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Feature importance
    feature_names = ["peminatan", "brand", "posisi"]
    feature_importance = dict(zip(feature_names, model.feature_importances_.tolist()))

    # Print results
    print(f"\n  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall_val:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"\n  Classification Report:\n{report_text}")
    print(f"  Confusion Matrix:\n{cm}")
    print(f"\n  Feature Importance: {feature_importance}")

    # Step 4: Stratified K-Fold Cross-Validation
    print("\n[Step 4] Stratified K-Fold Cross-Validation (5-fold)...")
    X_full = np.vstack([X_train, X_test])
    y_full = np.concatenate([y_train, y_test])

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_scores = cross_val_score(model, X_full, y_full, cv=skf, scoring="accuracy")

    cv_mean = float(cv_scores.mean())
    cv_std = float(cv_scores.std())

    print(f"  CV Fold scores: {[f'{s:.4f}' for s in cv_scores]}")
    print(f"  CV Mean Accuracy: {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"  CV Accuracy Range: [{cv_mean - cv_std:.4f}, {cv_mean + cv_std:.4f}]")

    # Step 5: Save model
    print("\n[Step 5] Saving model...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"  Model saved to: {MODEL_PATH}")

    # Step 6: Invalidate prediction cache
    try:
        from app.ml.predict import invalidate_cache
        invalidate_cache()
        print("  Prediction cache invalidated.")
    except ImportError:
        pass

    # Compile results
    results = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall_val, 4),
        "f1_score": round(f1, 4),
        "cv_mean_accuracy": round(cv_mean, 4),
        "cv_std_accuracy": round(cv_std, 4),
        "cv_fold_scores": [round(float(s), 4) for s in cv_scores],
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "feature_importance": feature_importance,
        "n_estimators": n_estimators,
        "train_size": X_train.shape[0],
        "test_size": X_test.shape[0],
        "dataset_size": X_train.shape[0] + X_test.shape[0],
        "class_names": class_names
    }

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    return results


if __name__ == "__main__":
    """Allow running training directly from command line."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    results = train_model()
    print(f"\nFinal accuracy: {results['accuracy']*100:.2f}%")
    print(f"CV accuracy: {results['cv_mean_accuracy']*100:.2f}% ± {results['cv_std_accuracy']*100:.2f}%")
