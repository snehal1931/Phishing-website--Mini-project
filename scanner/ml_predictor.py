"""
ML Predictor — loads the trained Random Forest model and predicts
whether a URL is 'Phishing' or 'Safe', along with confidence %.
"""
import os
import joblib
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / 'ml_model' / 'phishing_model.pkl'
_model = None


def load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run: py ml_model/train_model.py"
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict(feature_list: list) -> dict:
    """
    feature_list: ordered list of 16 numeric features
    Returns: {'result': 'Phishing'|'Safe', 'confidence': float 0-100}
    """
    model = load_model()
    X = np.array(feature_list).reshape(1, -1)
    prediction = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    # Label mapping: 0 = Safe, 1 = Phishing  (set during training)
    classes = list(model.classes_)
    if 1 in classes:
        phishing_idx = classes.index(1)
    else:
        phishing_idx = 0

    if prediction == 1:
        result = 'Phishing'
        confidence = round(proba[phishing_idx] * 100, 1)
    else:
        result = 'Safe'
        safe_idx = 1 - phishing_idx
        confidence = round(proba[safe_idx] * 100, 1)

    return {'result': result, 'confidence': confidence}
