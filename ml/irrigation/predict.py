# ─── AgriFlow AI — Irrigation ML Predictor (Phase 19) ────────────────────────
"""
ML-based irrigation advisor.
Falls back to rule engine if model is not trained.

If training data is available:
  cd ml && python -m irrigation.train

Input features:
  soilMoisture, temperature, humidity, rainProbability,
  cropType, growthStage, soilType, recentRainfall
"""
from pathlib import Path
import json

ML_ROOT   = Path(__file__).resolve().parent.parent
MODEL_DIR = ML_ROOT / "model" / "irrigation"
MODEL_PATH  = MODEL_DIR / "irrigation_model.pkl"
ENCODER_PATH = MODEL_DIR / "encoder.pkl"
CONFIG_PATH  = MODEL_DIR / "config.json"


class IrrigationAdvisor:
    """
    ML-based irrigation decision model.
    Outputs: IRRIGATE | WAIT | REDUCE IRRIGATION
    """

    def __init__(self):
        self.model   = None
        self.encoder = None
        self._load()

    def _load(self):
        if MODEL_PATH.exists():
            import pickle
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            if ENCODER_PATH.exists():
                with open(ENCODER_PATH, "rb") as f:
                    self.encoder = pickle.load(f)

    def advise(self, inputs: dict) -> dict:
        if self.model is None:
            # Fall back to rule engine
            from irrigation_rules import rule_based_advice
            result = rule_based_advice(inputs)
            result["modelStatus"] = "RULE-BASED (ML model not trained)"
            return result

        import numpy as np
        features = np.array([[
            inputs.get("soilMoisture",    50.0),
            inputs.get("temperature",     25.0),
            inputs.get("humidity",        60.0),
            inputs.get("rainProbability", 0.0),
            inputs.get("recentRainfall",  0.0),
        ]])

        prediction = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0] if hasattr(self.model, "predict_proba") else None

        return {
            "decision": prediction,
            "reason": f"ML model prediction based on sensor inputs.",
            "risk": "Medium",
            "estimatedWaterImpact": "See decision above.",
            "factors": [
                f"Soil moisture: {inputs.get('soilMoisture')}%",
                f"Temperature: {inputs.get('temperature')}°C",
                f"Rain probability: {inputs.get('rainProbability')}%",
            ],
            "modelStatus": "ML",
        }
