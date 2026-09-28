import numpy as np
import joblib

from config import MODEL_FILE
from preprocessing import record_to_dataframe


class EdgeGuardModel:

    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):

        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_FILE}\n"
                "Run: python train_model.py"
            )

        self.model = joblib.load(MODEL_FILE)

    def predict(self, record):

        X = record_to_dataframe(record)

        prediction = self.model.predict(X)[0]

        label = str(prediction).upper()

        confidence = 0.0

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(X)[0]
            confidence = float(np.max(probabilities) * 100)

        if label == "NORMAL":
            health_score = 95.0
        elif label == "WARNING":
            health_score = 65.0
        else:
            health_score = 30.0

        return {
            "health_status": label,
            "confidence": round(confidence, 1),
            "health_score": health_score,
            "model_source": "SVM"
        }


_model = None


def get_model():

    global _model

    if _model is None:
        _model = EdgeGuardModel()

    return _model


def predict(record):

    return get_model().predict(record)