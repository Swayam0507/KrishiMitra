# ─── AgriFlow AI — Disease Prediction Interface (Phase 14) ────────────────────
"""
Official-style prediction interface.

Programmatic:
  from disease.predict import DiseasePredictor
  predictor = DiseasePredictor()
  result = predictor.predict("path/to/image.jpg")

CLI:
  python -m disease.predict --image path/to/image.jpg

Output: class_label + confidence + risk + recommendations

If model not trained:
  Returns "MODEL NOT TRAINED" — never returns a fake prediction.
"""
import sys
import json
import argparse
from pathlib import Path
import torch
import torch.nn.functional as F
from PIL import Image

from .config import CONFIG, DiseaseModelConfig
from .dataset import build_transforms
from .model import load_model_for_inference


# ─── Risk mapping ──────────────────────────────────────────────────────────────
# Keywords in class names → risk level + recommendations
DISEASE_RISK_MAP: dict[str, dict] = {
    "healthy": {
        "risk": "LOW",
        "recommendations": [
            "Crop appears healthy. Maintain current practices.",
            "Continue routine monitoring.",
        ],
    },
    "blight": {
        "risk": "HIGH",
        "recommendations": [
            "Remove and destroy infected leaves immediately.",
            "Apply appropriate fungicide as per label instructions.",
            "Avoid overhead irrigation to prevent spore spread.",
            "Improve air circulation between plants.",
        ],
    },
    "spot": {
        "risk": "MEDIUM",
        "recommendations": [
            "Remove affected leaves and dispose safely.",
            "Apply copper-based fungicide.",
            "Monitor closely over next 7 days.",
        ],
    },
    "mold": {
        "risk": "HIGH",
        "recommendations": [
            "Improve ventilation and reduce humidity.",
            "Apply recommended fungicide.",
            "Reduce irrigation frequency.",
        ],
    },
    "rust": {
        "risk": "MEDIUM",
        "recommendations": [
            "Apply systemic fungicide for rust control.",
            "Remove heavily infected tissue.",
        ],
    },
    "virus": {
        "risk": "HIGH",
        "recommendations": [
            "No cure for viral infections — remove infected plants to prevent spread.",
            "Control insect vectors (aphids, whiteflies) with appropriate insecticide.",
            "Use virus-free planting material in future seasons.",
        ],
    },
    "scab": {
        "risk": "MEDIUM",
        "recommendations": [
            "Apply fungicide at early infection stage.",
            "Maintain proper spacing for air circulation.",
        ],
    },
    "rot": {
        "risk": "HIGH",
        "recommendations": [
            "Remove and destroy infected plant parts immediately.",
            "Improve drainage to prevent waterlogging.",
            "Apply copper-based or recommended fungicide.",
        ],
    },
    "curl": {
        "risk": "MEDIUM",
        "recommendations": [
            "Check for viral infection or mite infestation.",
            "Apply miticide if mites are detected.",
            "Consult an agronomist for diagnosis.",
        ],
    },
    "default": {
        "risk": "MEDIUM",
        "recommendations": [
            "Consult a qualified agronomist for diagnosis.",
            "Monitor crop closely over the next 7 days.",
            "Take additional samples for laboratory analysis.",
        ],
    },
}


def _get_risk_and_recommendations(class_label: str) -> tuple[str, list[str]]:
    """Map class label to risk level and recommendations."""
    label_lower = class_label.lower()
    for keyword, info in DISEASE_RISK_MAP.items():
        if keyword in label_lower:
            return info["risk"], info["recommendations"]
    return DISEASE_RISK_MAP["default"]["risk"], DISEASE_RISK_MAP["default"]["recommendations"]


class DiseasePredictor:
    """
    Stateful disease predictor — loads model once, reuses for multiple predictions.
    """

    def __init__(self, config: DiseaseModelConfig = CONFIG):
        self.config = config
        self.model = None
        self.class_names = []
        self.status = "NOT_INITIALIZED"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load()

    def _load(self):
        model, class_names, status = load_model_for_inference(self.config)
        self.model = model
        self.class_names = class_names
        self.status = status
        if model is not None:
            self.model = model.to(self.device)
            self.transform = build_transforms("val", self.config)

    def predict(self, image_path: str) -> dict:
        """
        Predict disease from image path.

        Returns dict with:
          class_label, confidence, risk, recommendations, model_status, top3

        NEVER returns a fake prediction.
        If model not trained: model_status = "MODEL NOT TRAINED"
        """
        # ─ Model check ────────────────────────────────────────────────────────
        if self.model is None:
            return {
                "class_label": None,
                "confidence": None,
                "risk": None,
                "recommendations": [],
                "model_status": "MODEL NOT TRAINED",
                "top3": [],
                "message": "Train the model first: cd ml && python -m disease.train",
            }

        # ─ File validation ────────────────────────────────────────────────────
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
            raise ValueError(f"Unsupported image format: {path.suffix}")

        # ─ Load and preprocess image ──────────────────────────────────────────
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Could not read image: {e}")

        tensor = self.transform(img).unsqueeze(0).to(self.device)

        # ─ Inference ─────────────────────────────────────────────────────────
        self.model.eval()
        with torch.no_grad():
            logits = self.model(tensor)
            probs  = F.softmax(logits, dim=1)[0]

        confidence, pred_idx = probs.max(0)
        confidence = float(confidence.item())
        pred_idx   = int(pred_idx.item())

        class_label = self.class_names[pred_idx] if pred_idx < len(self.class_names) else "Unknown"
        risk, recommendations = _get_risk_and_recommendations(class_label)

        # Top-3 predictions
        top3_vals, top3_idxs = probs.topk(min(3, len(self.class_names)))
        top3 = [
            {
                "class": self.class_names[int(i)] if int(i) < len(self.class_names) else "Unknown",
                "confidence": round(float(v), 4),
            }
            for v, i in zip(top3_vals, top3_idxs)
        ]

        # Low confidence warning
        model_status = "PREDICTED"
        if confidence < 0.5:
            model_status = "LOW_CONFIDENCE"
            recommendations = [
                "⚠ Model confidence is low — please upload a clearer, well-lit image.",
                "Consider taking a closer photo of the affected area.",
            ] + recommendations[:2]

        return {
            "class_label":     class_label,
            "confidence":      round(confidence, 4),
            "risk":            risk,
            "recommendations": recommendations,
            "model_status":    model_status,
            "top3":            top3,
            "gradcam_path":    None,  # filled by gradcam.py
        }


# ─── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AgriFlow AI — Crop Disease Prediction")
    parser.add_argument("--image", required=True, help="Path to leaf image")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    predictor = DiseasePredictor()
    result = predictor.predict(args.image)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("\n" + "=" * 50)
    print("  AgriFlow AI — Disease Detection Result")
    print("=" * 50)

    if result["model_status"] == "MODEL NOT TRAINED":
        print(f"\n  STATUS: MODEL NOT TRAINED")
        print(f"  {result.get('message', '')}")
    else:
        print(f"\n  Disease:    {result['class_label']}")
        print(f"  Confidence: {result['confidence']*100:.1f}%")
        print(f"  Risk:       {result['risk']}")
        print(f"  Status:     {result['model_status']}")
        print(f"\n  Recommendations:")
        for rec in result["recommendations"]:
            print(f"    • {rec}")
        print(f"\n  Top 3 predictions:")
        for t in result["top3"]:
            print(f"    {t['confidence']*100:.1f}%  {t['class']}")

    print("=" * 50)


if __name__ == "__main__":
    main()
