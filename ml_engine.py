import joblib
import os
import numpy as np
from preprocessing import extract_features

class EdgeGuardMLEngine:
    def __init__(self):
        self.model_path = "models/edgeguard_svm.pkl"
        self.scaler_path = "models/scaler.pkl"
        self.model = None
        self.scaler = None
        self.labels = {0: "NORMAL_OPERATION", 1: "EARLY_ABNORMALITY", 2: "CRITICAL_FAULT"}
        self.load_models()

    def load_models(self):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            print("Warning: ML models not found. Run train_model.py first. Using heuristic fallback.")

    def predict(self, temp, current, vib_rms):
        """
        Returns (Classification String, Confidence Float)
        """
        if self.model and self.scaler:
            try:
                features = extract_features(temp, current, vib_rms)
                features_scaled = self.scaler.transform(features)
                
                prediction = self.model.predict(features_scaled)[0]
                probabilities = self.model.predict_proba(features_scaled)[0]
                
                class_label = self.labels.get(prediction, "UNKNOWN")
                confidence = float(np.max(probabilities))
                
                return class_label, confidence
            except Exception as e:
                print(f"ML Prediction error: {e}")
                
        # Fallback Heuristics if model is missing
        return self._heuristic_fallback(temp, current, vib_rms)

    def _heuristic_fallback(self, temp, current, vib_rms):
        if temp > 80 or current > 2.5 or vib_rms > 0.7:
            return "CRITICAL_FAULT", 0.95
        elif temp > 60 or current > 1.5 or vib_rms > 0.3:
            return "EARLY_ABNORMALITY", 0.90
        else:
            return "NORMAL_OPERATION", 0.98