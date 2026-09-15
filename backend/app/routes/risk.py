# ─── AgriFlow AI — Disease Risk Engine ───────────────────────────────────────
"""
Computes a 0–100 disease-risk score from agronomic inputs.
This is a transparent, rule-based scoring engine — no fake ML predictions.
Each factor is documented so the score is explainable during an interview.

Risk bands:
  0–30   → Low
  31–65  → Medium
  66–100 → High
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()

# ─── Request / Response schemas ───────────────────────────────────────────────

class RiskRequest(BaseModel):
    crop: str = Field(..., description="e.g. Tomato, Rice, Wheat")
    cropStage: str = Field(..., description="Seed/Germination/Vegetative/Flowering/Fruiting/Harvest")
    temperature: float = Field(..., description="°C")
    humidity: float = Field(..., ge=0, le=100, description="%")
    rainfall: float = Field(default=0.0, ge=0, description="mm in last 24 h")
    hasDiseaseHistory: bool = Field(default=False, description="Previous disease on this crop/plot")
    currentDiseaseConfidence: Optional[float] = Field(
        default=None, ge=0, le=1,
        description="Confidence of the most recent disease prediction (0–1), if any"
    )
    plotId: Optional[str] = None
    farmId: Optional[str] = None


# ─── Scoring logic ────────────────────────────────────────────────────────────

# Crop-specific base vulnerability (0–20 extra points)
CROP_VULNERABILITY: dict[str, int] = {
    "tomato": 18, "potato": 16, "rice": 15, "grape": 20,
    "wheat": 10, "corn": 8, "maize": 8, "cotton": 12,
    "soybean": 10, "groundnut": 12, "sugarcane": 10,
}

# Growth stages that are most susceptible
HIGH_RISK_STAGES = {"Flowering", "Fruiting"}
MEDIUM_RISK_STAGES = {"Vegetative"}

# Temperature ranges favourable to fungal/bacterial disease (°C)
TEMP_DISEASE_RANGE = (18.0, 30.0)


def _compute_risk(data: RiskRequest) -> dict:
    """
    Returns score (int 0–100) + list of factor strings.
    """
    score = 0
    factors: list[str] = []

    # ── Humidity ──────────────────────────────────────────────────────────────
    if data.humidity >= 90:
        score += 28
        factors.append(f"Very high humidity ({data.humidity:.0f}%) — ideal for fungal spread")
    elif data.humidity >= 80:
        score += 20
        factors.append(f"High humidity ({data.humidity:.0f}%) — favourable for disease")
    elif data.humidity >= 70:
        score += 10
        factors.append(f"Moderate-high humidity ({data.humidity:.0f}%)")

    # ── Temperature ───────────────────────────────────────────────────────────
    if TEMP_DISEASE_RANGE[0] <= data.temperature <= TEMP_DISEASE_RANGE[1]:
        score += 15
        factors.append(
            f"Temperature ({data.temperature:.1f}°C) in disease-prone range ({TEMP_DISEASE_RANGE[0]}–{TEMP_DISEASE_RANGE[1]}°C)"
        )
    elif data.temperature > 35:
        score += 5
        factors.append(f"High temperature ({data.temperature:.1f}°C) — heat stress may reduce plant immunity")

    # ── Rainfall ──────────────────────────────────────────────────────────────
    if data.rainfall >= 20:
        score += 20
        factors.append(f"Heavy recent rainfall ({data.rainfall:.1f} mm) — waterlogging risk")
    elif data.rainfall >= 10:
        score += 15
        factors.append(f"Moderate recent rainfall ({data.rainfall:.1f} mm) — increased moisture")
    elif data.rainfall > 0:
        score += 5
        factors.append(f"Light recent rainfall ({data.rainfall:.1f} mm)")

    # ── Crop stage ────────────────────────────────────────────────────────────
    if data.cropStage in HIGH_RISK_STAGES:
        score += 15
        factors.append(f"Susceptible crop stage: {data.cropStage} — plants more vulnerable")
    elif data.cropStage in MEDIUM_RISK_STAGES:
        score += 8
        factors.append(f"Moderately vulnerable crop stage: {data.cropStage}")

    # ── Crop vulnerability ────────────────────────────────────────────────────
    crop_key = data.crop.lower().strip()
    vuln = CROP_VULNERABILITY.get(crop_key, 5)
    if vuln > 0:
        score += vuln
        factors.append(f"{data.crop} — base vulnerability score {vuln}/20")

    # ── Disease history ───────────────────────────────────────────────────────
    if data.hasDiseaseHistory:
        score += 20
        factors.append("Previous disease recorded on this crop/plot — elevated risk")

    # ── Current AI prediction confidence ─────────────────────────────────────
    if data.currentDiseaseConfidence is not None:
        if data.currentDiseaseConfidence >= 0.85:
            score += 25
            factors.append(
                f"Disease detected with high confidence ({data.currentDiseaseConfidence*100:.0f}%)"
            )
        elif data.currentDiseaseConfidence >= 0.60:
            score += 15
            factors.append(
                f"Disease suspected — moderate confidence ({data.currentDiseaseConfidence*100:.0f}%)"
            )

    # ── Clamp ─────────────────────────────────────────────────────────────────
    score = min(score, 100)

    # ── Risk band ─────────────────────────────────────────────────────────────
    if score >= 66:
        risk_band = "High"
        actions = [
            "Inspect crop immediately for disease symptoms.",
            "Prepare fungicide/bactericide as a precaution.",
            "Improve field drainage to reduce waterlogging.",
            "Notify agronomist for field visit.",
        ]
    elif score >= 31:
        risk_band = "Medium"
        actions = [
            "Monitor crop closely over the next 48 hours.",
            "Ensure adequate spacing for air circulation.",
            "Avoid overhead irrigation to reduce leaf wetness.",
        ]
    else:
        risk_band = "Low"
        actions = [
            "Routine monitoring is sufficient.",
            "Maintain good field hygiene.",
        ]

    return {
        "riskScore": score,
        "riskBand": risk_band,
        "factors": factors,
        "recommendedActions": actions,
    }


# ─── API Endpoints ────────────────────────────────────────────────────────────

@router.post("/assess")
async def assess_risk(data: RiskRequest, user=Depends(get_current_user)):
    """
    Compute disease risk score.
    Saves the assessment to MongoDB for historical tracking.
    """
    result = _compute_risk(data)

    db = get_database()
    doc = {
        "userId": str(user["_id"]),
        "inputs": data.model_dump(),
        **result,
        "createdAt": datetime.now(timezone.utc),
    }
    ins = await db.disease_risk.insert_one(doc)

    return {
        "id": str(ins.inserted_id),
        "crop": data.crop,
        "cropStage": data.cropStage,
        **result,
        "createdAt": doc["createdAt"],
        "note": "Score calculated using rule-based risk engine (not ML-fabricated)",
    }


@router.get("/history")
async def risk_history(
    plotId: Optional[str] = None,
    limit: int = 20,
    user=Depends(get_current_user),
):
    """Return past risk assessments for the current user."""
    db = get_database()
    query: dict = {"userId": str(user["_id"])}
    if plotId:
        query["inputs.plotId"] = plotId

    docs = await db.disease_risk.find(query).sort("createdAt", -1).limit(limit).to_list(limit)
    return [
        {
            "id": str(d["_id"]),
            "crop": d["inputs"].get("crop"),
            "cropStage": d["inputs"].get("cropStage"),
            "riskScore": d["riskScore"],
            "riskBand": d["riskBand"],
            "factors": d.get("factors", []),
            "createdAt": d.get("createdAt"),
        }
        for d in docs
    ]


@router.get("/summary")
async def risk_summary(user=Depends(get_current_user)):
    """Return summary counts by risk band for the current user."""
    db = get_database()
    docs = await db.disease_risk.find({"userId": str(user["_id"])}).to_list(500)
    counts = {"Low": 0, "Medium": 0, "High": 0}
    for d in docs:
        band = d.get("riskBand", "Low")
        if band in counts:
            counts[band] += 1

    latest = docs[0] if docs else None
    return {
        "totalAssessments": len(docs),
        "byRiskBand": counts,
        "latestRiskScore": latest["riskScore"] if latest else None,
        "latestRiskBand": latest["riskBand"] if latest else None,
    }
