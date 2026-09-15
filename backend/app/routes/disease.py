# ─── AgriFlow AI — Disease Detection Route ────────────────────────────────────
"""
POST /api/disease/predict
- Accepts image upload (multipart/form-data)
- Validates file type and size
- Runs prediction via ml/disease/predict.py
- Saves result to MongoDB
- Returns structured response

If model weights are not found:
  {"modelStatus": "MODEL NOT TRAINED", "disease": null, ...}

NEVER fabricates predictions.
"""
import os
import sys
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime, timezone
from typing import Optional

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()

UPLOAD_DIR = Path("uploads/disease")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE_MB = 10

# Path to the ML module (relative to project root)
ML_PATH = Path(__file__).resolve().parents[3] / "ml"


def _import_predictor():
    """Dynamically import the disease predictor to avoid hard dependency."""
    project_root = str(ML_PATH.parent)
    ml_dir = str(ML_PATH)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if ml_dir not in sys.path:
        sys.path.insert(0, ml_dir)

    try:
        try:
            from ml.disease.predict import DiseasePredictor
        except ImportError:
            from disease.predict import DiseasePredictor
        return DiseasePredictor()
    except Exception:
        return None



@router.post("/predict")
async def predict_disease(
    image: UploadFile = File(...),
    cropType: Optional[str] = Form(default=None),
    growthStage: Optional[str] = Form(default=None),
    user=Depends(get_current_user),
):
    # ── Validate file ──────────────────────────────────────────────────────────
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    content = await image.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit")

    # ── Save upload ────────────────────────────────────────────────────────────
    filename = f"{uuid.uuid4().hex}{suffix}"
    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as f:
        f.write(content)

    # ── Run prediction ─────────────────────────────────────────────────────────
    predictor = _import_predictor()

    if predictor is None:
        # ML module not importable — treat as not trained
        result = {
            "disease": None,
            "confidence": None,
            "risk": None,
            "recommendations": [],
            "modelStatus": "MODEL NOT TRAINED",
            "gradcamPath": None,
        }
    else:
        try:
            pred = predictor.predict(str(save_path))
            result = {
                "disease": pred.get("class_label"),
                "confidence": pred.get("confidence"),
                "risk": pred.get("risk"),
                "recommendations": pred.get("recommendations", []),
                "modelStatus": pred.get("model_status", "PREDICTED"),
                "gradcamPath": pred.get("gradcam_path"),
            }
        except Exception as exc:
            result = {
                "disease": None,
                "confidence": None,
                "risk": None,
                "recommendations": [],
                "modelStatus": f"ERROR: {exc}",
                "gradcamPath": None,
            }

    # ── Persist to MongoDB ─────────────────────────────────────────────────────
    db = get_database()
    history_doc = {
        "userId": str(user["_id"]),
        "imagePath": str(save_path),
        "cropType": cropType,
        "growthStage": growthStage,
        **result,
        "createdAt": datetime.now(timezone.utc),
    }
    ins = await db.disease_predictions.insert_one(history_doc)

    return {
        "id": str(ins.inserted_id),
        "imagePath": str(save_path),
        "cropType": cropType,
        "growthStage": growthStage,
        **result,
        "createdAt": history_doc["createdAt"],
    }


@router.get("/history")
async def prediction_history(user=Depends(get_current_user)):
    """Return past disease predictions for the current user."""
    db = get_database()
    docs = await db.disease_predictions.find(
        {"userId": str(user["_id"])}
    ).sort("createdAt", -1).to_list(50)

    return [
        {
            "id": str(d["_id"]),
            "disease": d.get("disease"),
            "confidence": d.get("confidence"),
            "risk": d.get("risk"),
            "cropType": d.get("cropType"),
            "growthStage": d.get("growthStage"),
            "modelStatus": d.get("modelStatus"),
            "createdAt": d.get("createdAt"),
        }
        for d in docs
    ]
