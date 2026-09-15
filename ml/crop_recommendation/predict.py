# ─── AgriFlow AI — Crop Recommendation Predictor ─────────────────────────────
import json
import pickle
import numpy as np
from pathlib import Path
from typing import Optional

ML_ROOT   = Path(__file__).resolve().parent.parent
MODEL_DIR = ML_ROOT / "model" / "crop_recommendation"
MODEL_PATH   = MODEL_DIR / "crop_recommender.pkl"
SCALER_PATH  = MODEL_DIR / "scaler.pkl"
CLASSES_PATH = MODEL_DIR / "classes.json"

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

CROP_NOTES = {
    "rice":       "Requires high water availability and warm, humid climate.",
    "wheat":      "Grows best in cool, dry climates with moderate rainfall.",
    "maize":      "Adaptable crop, needs warm temperatures and moderate water.",
    "cotton":     "Requires hot, dry climate with good drainage.",
    "sugarcane":  "Needs abundant water and high humidity.",
    "tomato":     "Warm climate, well-drained soil, regular irrigation.",
    "potato":     "Cool climate, loamy soil, moderate moisture.",
    "grapes":     "Warm, dry climate; sensitive to excess moisture.",
    "mango":      "Tropical fruit; drought-tolerant once established.",
    "banana":     "Tropical; high water and nutrient demand.",
}


class CropPredictor:
    def __init__(self):
        self.model  = None
        self.scaler = None
        self.classes = []
        self._load()

    def _load(self):
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            with open(MODEL_PATH,  "rb") as f: self.model  = pickle.load(f)
            with open(SCALER_PATH, "rb") as f: self.scaler = pickle.load(f)
            if CLASSES_PATH.exists():
                with open(CLASSES_PATH) as f:
                    self.classes = json.load(f)

    def predict(self, inputs: dict) -> dict:
        if self.model is None:
            return {
                "recommendation": None,
                "score": None,
                "reason": "MODEL NOT TRAINED",
                "alternatives": [],
                "modelStatus": "MODEL NOT TRAINED",
            }

        features = np.array([[
            inputs.get("nitrogen",    inputs.get("N",    50)),
            inputs.get("phosphorus",  inputs.get("P",    50)),
            inputs.get("potassium",   inputs.get("K",    50)),
            inputs.get("temperature", 25),
            inputs.get("humidity",    60),
            inputs.get("ph",          7.0),
            inputs.get("rainfall",    100),
        ]])

        features_scaled = self.scaler.transform(features)
        probs = self.model.predict_proba(features_scaled)[0]
        top3_idx = np.argsort(probs)[::-1][:3]

        top_crop  = self.classes[top3_idx[0]]
        top_score = round(float(probs[top3_idx[0]]), 4)

        note = CROP_NOTES.get(top_crop.lower(), "Consult local agronomist for planting guidance.")

        return {
            "recommendation": top_crop,
            "score": top_score,
            "reason": (
                f"Based on N={inputs.get('nitrogen',inputs.get('N',50))}, "
                f"P={inputs.get('phosphorus',inputs.get('P',50))}, "
                f"K={inputs.get('potassium',inputs.get('K',50))}, "
                f"pH={inputs.get('ph',7.0)}, "
                f"Temp={inputs.get('temperature',25)}°C, "
                f"Humidity={inputs.get('humidity',60)}%, "
                f"Rainfall={inputs.get('rainfall',100)}mm — "
                f"{note}"
            ),
            "alternatives": [
                {
                    "crop": self.classes[top3_idx[i]],
                    "score": round(float(probs[top3_idx[i]]), 4),
                }
                for i in range(1, len(top3_idx))
            ],
            "modelStatus": "PREDICTED",
        }
