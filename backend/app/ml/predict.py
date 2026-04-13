"""
Prediction Module
=================
Handles loading the trained model and making predictions with
explainable AI features (feature importance + human-readable explanations).

Uses singleton caching to avoid reloading model/encoders from disk
on every prediction request.
"""

import os
import json
import numpy as np
import joblib

from app.config import MODEL_PATH, ENCODERS_PATH, PRODUCT_CATALOG_PATH

# Feature names used during training
FEATURE_NAMES = ["peminatan", "brand", "posisi"]

# Human-readable labels for explanations (Indonesian)
FEATURE_LABELS = {
    "peminatan": "Gaya Bermain (Peminatan)",
    "brand": "Merek Sepatu (Brand)",
    "posisi": "Posisi Pemain (Posisi)"
}

LABEL_DESCRIPTIONS = {
    "speed_boot": "Speed Boot - Sepatu yang dirancang untuk kecepatan dan akselerasi tinggi",
    "control_boot": "Control Boot - Sepatu yang dirancang untuk kontrol bola dan passing presisi",
    "power_boot": "Power Boot - Sepatu yang dirancang untuk tendangan keras dan stabilitas"
}

# ==========================================
# MODEL CACHE (Singleton Pattern)
# ==========================================
_cached_model = None
_cached_encoders = None


def invalidate_cache():
    """
    Invalidate the cached model and encoders.
    Called after model retraining so the next prediction loads the new model.
    """
    global _cached_model, _cached_encoders
    _cached_model = None
    _cached_encoders = None


def _get_model():
    """
    Get the trained model, loading from disk only on first call or after
    cache invalidation.

    Returns:
        sklearn.ensemble.RandomForestClassifier: Trained model

    Raises:
        FileNotFoundError: If model file doesn't exist
    """
    global _cached_model
    if _cached_model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model not found at: {MODEL_PATH}. "
                "Please train the model first via the admin panel."
            )
        _cached_model = joblib.load(MODEL_PATH)
    return _cached_model


def _get_encoders():
    """
    Get the fitted encoders, loading from disk only on first call or after
    cache invalidation.

    Returns:
        dict: Dictionary of LabelEncoders

    Raises:
        FileNotFoundError: If encoders file doesn't exist
    """
    global _cached_encoders
    if _cached_encoders is None:
        if not os.path.exists(ENCODERS_PATH):
            raise FileNotFoundError(
                f"Encoders not found at: {ENCODERS_PATH}. "
                "Please train the model first."
            )
        _cached_encoders = joblib.load(ENCODERS_PATH)
    return _cached_encoders


def _get_top_shoe_names(predicted_class: str, brand: str, max_shoes: int = 3):
    """
    Get the top shoe model names from the product catalog for the explanation.

    Args:
        predicted_class: The predicted boot category
        brand: The user's preferred brand
        max_shoes: Maximum number of shoe names to return

    Returns:
        list: List of shoe name strings
    """
    try:
        if not os.path.exists(PRODUCT_CATALOG_PATH):
            return []

        with open(PRODUCT_CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)

        brand_lower = brand.lower()
        shoes = []

        if predicted_class in catalog and brand_lower in catalog[predicted_class]:
            for product in catalog[predicted_class][brand_lower][:max_shoes]:
                shoes.append(product.get("name", "Unknown"))

        return shoes
    except Exception:
        return []


def predict(peminatan: str, brand: str, posisi: str):
    """
    Make a prediction for a single input and return comprehensive results
    including classification, probabilities, and explainable AI features.

    Args:
        peminatan: Play style preference (speed/control/power)
        brand: Preferred brand (nike/adidas/puma/mizuno/umbro)
        posisi: Player position (striker/midfielder/defender/goalkeeper)

    Returns:
        dict: Prediction results containing:
            - predicted_class: The predicted boot category
            - predicted_label: Human-readable label
            - probabilities: Dict of class -> probability percentage
            - feature_importance: Dict of feature -> importance value
            - explanation: Human-readable AI explanation text (Indonesian)
    """
    # Load model and encoders (cached singleton)
    model = _get_model()
    encoders = _get_encoders()

    # Encode input
    encoded_input = np.array([
        encoders["peminatan"].transform([peminatan.lower()])[0],
        encoders["brand"].transform([brand.lower()])[0],
        encoders["posisi"].transform([posisi.lower()])[0]
    ]).reshape(1, -1)

    # Make prediction
    predicted_class_encoded = model.predict(encoded_input)[0]
    predicted_class = encoders["label_sepatu"].inverse_transform([predicted_class_encoded])[0]

    # Get prediction probabilities
    probabilities_raw = model.predict_proba(encoded_input)[0]
    class_names = encoders["label_sepatu"].classes_
    probabilities = {
        name: round(float(prob) * 100, 2)
        for name, prob in zip(class_names, probabilities_raw)
    }

    # Get feature importance from the trained model
    importance_values = model.feature_importances_
    feature_importance = {
        name: round(float(val), 4)
        for name, val in zip(FEATURE_NAMES, importance_values)
    }

    # Get specific shoe names for the explanation
    top_shoes = _get_top_shoe_names(predicted_class, brand)

    # Generate human-readable explanation (Indonesian)
    explanation = _generate_explanation(
        peminatan, brand, posisi,
        predicted_class, probabilities, feature_importance,
        top_shoes
    )

    return {
        "predicted_class": predicted_class,
        "predicted_label": LABEL_DESCRIPTIONS.get(predicted_class, predicted_class),
        "probabilities": probabilities,
        "feature_importance": feature_importance,
        "explanation": explanation,
        "input": {
            "peminatan": peminatan,
            "brand": brand,
            "posisi": posisi
        }
    }


def _generate_explanation(peminatan, brand, posisi, predicted_class,
                          probabilities, feature_importance, top_shoes=None):
    """
    Generate a human-readable explanation for the prediction (in Indonesian).

    This implements the Explainable AI requirement by translating model
    internals into understandable language, including specific shoe model
    recommendations.

    Args:
        peminatan: Input play style
        brand: Input brand
        posisi: Input position
        predicted_class: Model's prediction
        probabilities: Class probabilities
        feature_importance: Feature importance values
        top_shoes: List of top shoe model names for the predicted class

    Returns:
        str: Multi-sentence explanation in Indonesian
    """
    # Sort features by importance (highest first)
    sorted_features = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Map predicted class to Indonesian description
    class_map = {
        "speed_boot": "Speed Boot (Sepatu Kecepatan)",
        "control_boot": "Control Boot (Sepatu Kontrol)",
        "power_boot": "Power Boot (Sepatu Power)"
    }

    peminatan_map = {
        "speed": "kecepatan (speed)",
        "control": "kontrol (control)",
        "power": "kekuatan (power)"
    }

    posisi_map = {
        "striker": "Striker (Penyerang)",
        "midfielder": "Midfielder (Gelandang)",
        "defender": "Defender (Bek)",
        "goalkeeper": "Goalkeeper (Kiper)"
    }

    # Category-specific trait descriptions
    class_traits = {
        "speed_boot": "ringan, aerodinamis, dan dirancang untuk akselerasi maksimal",
        "control_boot": "bertekstur, responsif, dan dirancang untuk sentuhan bola presisi",
        "power_boot": "kokoh, stabil, dan dirancang untuk tendangan keras dan powerful"
    }

    # Build explanation
    explanation_parts = []

    # Main prediction sentence
    pred_label = class_map.get(predicted_class, predicted_class)
    confidence = probabilities.get(predicted_class, 0)
    explanation_parts.append(
        f"Berdasarkan analisis model Random Forest, sistem merekomendasikan "
        f"{pred_label} dengan tingkat kepercayaan {confidence:.1f}%."
    )

    # Input summary
    pem_label = peminatan_map.get(peminatan.lower(), peminatan)
    pos_label = posisi_map.get(posisi.lower(), posisi)
    explanation_parts.append(
        f"Rekomendasi ini didasarkan pada preferensi gaya bermain Anda yaitu "
        f"{pem_label}, merek pilihan {brand.title()}, dan posisi bermain "
        f"sebagai {pos_label}."
    )

    # Specific shoe recommendations in the explanation
    if top_shoes and len(top_shoes) > 0:
        traits = class_traits.get(predicted_class, "memiliki performa tinggi")
        if len(top_shoes) == 1:
            explanation_parts.append(
                f"Sepatu yang paling direkomendasikan untuk Anda adalah {top_shoes[0]}, "
                f"yang {traits}."
            )
        else:
            shoe_list = ", ".join(top_shoes[:-1]) + f", dan {top_shoes[-1]}"
            explanation_parts.append(
                f"Beberapa seri sepatu {brand.title()} yang direkomendasikan antara lain "
                f"{shoe_list}. Sepatu-sepatu ini {traits}."
            )

    # Feature importance explanation
    top_feature = sorted_features[0]
    top_feature_label = FEATURE_LABELS.get(top_feature[0], top_feature[0])
    top_importance_pct = round(top_feature[1] * 100, 1)

    explanation_parts.append(
        f"Faktor yang paling berpengaruh dalam rekomendasi ini adalah "
        f"{top_feature_label} dengan kontribusi sebesar {top_importance_pct}% "
        f"terhadap keputusan model."
    )

    # Secondary features
    if len(sorted_features) > 1:
        secondary_labels = [
            f"{FEATURE_LABELS.get(f[0], f[0])} ({round(f[1]*100, 1)}%)"
            for f in sorted_features[1:]
        ]
        explanation_parts.append(
            f"Faktor pendukung lainnya: {', '.join(secondary_labels)}."
        )

    return " ".join(explanation_parts)


def get_model_info():
    """
    Get information about the currently loaded model.

    Returns:
        dict: Model information including n_estimators, feature importance, etc.
    """
    try:
        model = _get_model()
        encoders = _get_encoders()

        return {
            "model_loaded": True,
            "n_estimators": model.n_estimators,
            "n_features": model.n_features_in_,
            "feature_names": FEATURE_NAMES,
            "feature_importance": {
                name: round(float(val), 4)
                for name, val in zip(FEATURE_NAMES, model.feature_importances_)
            },
            "classes": list(encoders["label_sepatu"].classes_)
        }
    except FileNotFoundError:
        return {"model_loaded": False}
