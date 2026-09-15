# ─── AgriFlow AI — Indicative Farm Health Score ───────────────────────────────
"""
Computes an INDICATIVE Farm Health Score (0–100) from multiple components.

⚠ This is NOT a scientifically validated agricultural measurement.
   It is a transparent, rule-based indicative score for farm management guidance.

Weights (sum = 100):
  Crop Health          → 30 %
  Disease Risk         → 25 %  (inverted: low risk = high score)
  Soil Condition       → 20 %
  Water Efficiency     → 15 %
  Activity Completion  → 10 %

Formula is fully documented so it can be explained in any interview.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()


# ─── Request ──────────────────────────────────────────────────────────────────

class HealthScoreRequest(BaseModel):
    farmId: str

    # Crop health inputs (0–100)
    activeCropPercent: float = Field(
        ..., ge=0, le=100,
        description="% of plots with an active crop"
    )
    cropStageProgress: float = Field(
        default=50.0, ge=0, le=100,
        description="Average % progress through crop lifecycle"
    )

    # Disease (0–100 risk score from /api/risk)
    latestRiskScore: Optional[float] = Field(
        default=None, ge=0, le=100,
        description="Most recent disease risk score; null if none"
    )

    # Soil condition (0–14 pH, 0–100 moisture)
    soilPH: Optional[float] = Field(default=7.0, ge=0, le=14)
    soilMoisture: Optional[float] = Field(default=50.0, ge=0, le=100)

    # Water efficiency (0–100 %)
    irrigationEfficiency: Optional[float] = Field(
        default=70.0, ge=0, le=100,
        description="Drip=90, Sprinkler=75, Flood=50, Rain-fed=40 (approx)"
    )

    # Activity completion (0–100 %)
    activityCompletionRate: Optional[float] = Field(
        default=50.0, ge=0, le=100,
        description="% of pending activities marked Completed in last 30 days"
    )


# ─── Component scorers ────────────────────────────────────────────────────────

def _score_crop_health(active_pct: float, stage_progress: float) -> float:
    """
    Score based on how many plots have active crops and how far along they are.
      active_pct     → 60 % weight
      stage_progress → 40 % weight
    """
    return round(active_pct * 0.6 + stage_progress * 0.4, 1)


def _score_disease_risk(risk_score: Optional[float]) -> float:
    """
    Invert disease risk score: high risk → low health component.
      Disease Risk 0   → component 100
      Disease Risk 100 → component 0
    No risk history → assume neutral 65.
    """
    if risk_score is None:
        return 65.0
    return round(max(0.0, 100.0 - risk_score), 1)


def _score_soil(ph: float, moisture: float) -> float:
    """
    pH optimal range 6.0–7.5 → 100.  Penalise outside this range.
    Moisture optimal range 40–70 % → 100. Penalise outside.
    Equal weight.
    """
    # pH score
    if 6.0 <= ph <= 7.5:
        ph_score = 100.0
    elif 5.5 <= ph < 6.0 or 7.5 < ph <= 8.0:
        ph_score = 75.0
    elif 5.0 <= ph < 5.5 or 8.0 < ph <= 8.5:
        ph_score = 50.0
    else:
        ph_score = 25.0

    # Moisture score
    if 40 <= moisture <= 70:
        m_score = 100.0
    elif 30 <= moisture < 40 or 70 < moisture <= 80:
        m_score = 70.0
    elif 20 <= moisture < 30 or 80 < moisture <= 90:
        m_score = 40.0
    else:
        m_score = 15.0

    return round((ph_score + m_score) / 2, 1)


def _score_water(efficiency: float) -> float:
    return round(efficiency, 1)


def _score_activity(completion_rate: float) -> float:
    return round(completion_rate, 1)


# ─── Main computation ─────────────────────────────────────────────────────────

WEIGHTS = {
    "cropHealth":          0.30,
    "diseaseRisk":         0.25,
    "soilCondition":       0.20,
    "waterEfficiency":     0.15,
    "activityCompletion":  0.10,
}

COMPONENT_LABELS = {
    "cropHealth":          "Crop Health",
    "diseaseRisk":         "Disease Risk (inverted)",
    "soilCondition":       "Soil Condition",
    "waterEfficiency":     "Water Efficiency",
    "activityCompletion":  "Activity Completion",
}


def _compute(data: HealthScoreRequest) -> dict:
    components = {
        "cropHealth":          _score_crop_health(data.activeCropPercent, data.cropStageProgress),
        "diseaseRisk":         _score_disease_risk(data.latestRiskScore),
        "soilCondition":       _score_soil(data.soilPH or 7.0, data.soilMoisture or 50.0),
        "waterEfficiency":     _score_water(data.irrigationEfficiency or 70.0),
        "activityCompletion":  _score_activity(data.activityCompletionRate or 50.0),
    }

    overall = round(
        sum(components[k] * WEIGHTS[k] for k in components), 1
    )

    if overall >= 75:
        grade, description = "Good", "Farm is in good condition. Keep up current practices."
    elif overall >= 50:
        grade, description = "Fair", "Farm health is acceptable. Focus on low-scoring components."
    elif overall >= 30:
        grade, description = "Poor", "Multiple components need attention. Prioritise disease risk and soil."
    else:
        grade, description = "Critical", "Immediate action required across several areas."

    # Improvement suggestions for lowest component
    sorted_components = sorted(components.items(), key=lambda x: x[1])
    weakest_key, weakest_val = sorted_components[0]
    suggestions = _suggestions_for(weakest_key, weakest_val)

    return {
        "overallScore": overall,
        "grade": grade,
        "description": description,
        "components": {
            k: {
                "label": COMPONENT_LABELS[k],
                "score": v,
                "weight": f"{int(WEIGHTS[k]*100)}%",
                "contribution": round(v * WEIGHTS[k], 1),
            }
            for k, v in components.items()
        },
        "weights": WEIGHTS,
        "weakestComponent": COMPONENT_LABELS[weakest_key],
        "improvementSuggestions": suggestions,
    }


def _suggestions_for(key: str, score: float) -> list[str]:
    suggestions_map = {
        "cropHealth": [
            "Plant crops in unused plots to increase active crop percentage.",
            "Monitor crop lifecycle stages and update records regularly.",
        ],
        "diseaseRisk": [
            "Run a disease risk assessment — disease risk is elevating this component.",
            "Improve field hygiene and monitor humidity levels.",
        ],
        "soilCondition": [
            "Test soil pH and apply lime/sulphur to correct imbalance.",
            "Adjust irrigation schedule to maintain optimal soil moisture (40–70%).",
        ],
        "waterEfficiency": [
            "Consider switching to drip irrigation for higher water efficiency.",
            "Reduce flood irrigation — it scores 50% efficiency vs. drip at 90%.",
        ],
        "activityCompletion": [
            "Complete pending farm activities to improve this component score.",
            "Assign activities to specific workers with due dates.",
        ],
    }
    return suggestions_map.get(key, ["Review and improve this component."])


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/score")
async def compute_health_score(data: HealthScoreRequest, user=Depends(get_current_user)):
    """
    Compute the INDICATIVE Farm Health Score.
    Saves to MongoDB for trend tracking.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(data.farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    result = _compute(data)

    doc = {
        "userId": str(user["_id"]),
        "farmId": data.farmId,
        "inputs": data.model_dump(),
        **result,
        "createdAt": datetime.now(timezone.utc),
        "disclaimer": "INDICATIVE Farm Health Score — not a scientifically validated measurement.",
    }
    ins = await db.farm_health_scores.insert_one(doc)

    return {
        "id": str(ins.inserted_id),
        "farmId": data.farmId,
        **result,
        "createdAt": doc["createdAt"],
        "disclaimer": doc["disclaimer"],
    }


@router.get("/{farm_id}/history")
async def health_score_history(
    farm_id: str,
    limit: int = Query(default=30, le=90),
    user=Depends(get_current_user),
):
    """Return historical health scores for trend display."""
    db = get_database()
    farm = await db.farms.find_one(
        {"_id": ObjectId(farm_id), "ownerId": user["_id"]}
    )
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    docs = await db.farm_health_scores.find(
        {"farmId": farm_id, "userId": str(user["_id"])}
    ).sort("createdAt", -1).limit(limit).to_list(limit)

    return [
        {
            "id": str(d["_id"]),
            "overallScore": d["overallScore"],
            "grade": d["grade"],
            "createdAt": d["createdAt"],
            "components": {k: v["score"] for k, v in d.get("components", {}).items()},
        }
        for d in reversed(docs)  # ascending for chart
    ]


@router.get("/{farm_id}/latest")
async def latest_health_score(farm_id: str, user=Depends(get_current_user)):
    """Return the most recent health score for a farm."""
    db = get_database()
    doc = await db.farm_health_scores.find_one(
        {"farmId": farm_id, "userId": str(user["_id"])},
        sort=[("createdAt", -1)],
    )
    if not doc:
        return {"message": "No health score computed yet for this farm.", "overallScore": None}

    return {
        "id": str(doc["_id"]),
        "farmId": farm_id,
        "overallScore": doc["overallScore"],
        "grade": doc["grade"],
        "description": doc["description"],
        "components": doc.get("components", {}),
        "weakestComponent": doc.get("weakestComponent"),
        "improvementSuggestions": doc.get("improvementSuggestions", []),
        "createdAt": doc["createdAt"],
        "disclaimer": doc.get("disclaimer"),
    }
