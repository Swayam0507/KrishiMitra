# ─── AgriFlow AI — Sustainability Score (Bonus Module D) ──────────────────────
"""
Computes an INDICATIVE Sustainability Score (0–100).

⚠ All savings estimates are ESTIMATED based on common agricultural benchmarks.
  They are not actual measurements.

Component weights (sum = 100 %):
  Water Efficiency      35 %
  Resource Efficiency   25 %
  Crop Health           25 %
  Soil Management       15 %

Formula is fully documented and reproducible.

Dataset references:
  - FAO irrigation efficiency benchmarks
  - ICAR soil health card guidelines
  - General agricultural practice scoring
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()


# ─── Request ──────────────────────────────────────────────────────────────────

class SustainabilityRequest(BaseModel):
    farmId: str

    # Water efficiency
    irrigationType: str = Field(
        default="Drip",
        description="Drip|Sprinkler|Flood|Furrow|Rain-fed|Canal"
    )
    waterUsageLitresPerAcre: Optional[float] = Field(
        default=None, ge=0,
        description="Actual water used (litres/acre/day). Leave null if unknown."
    )

    # Resource efficiency
    chemicalPesticidesUsed: bool = Field(default=True)
    organicFertilizerPercent: float = Field(
        default=0.0, ge=0, le=100,
        description="% of fertiliser that is organic"
    )
    croppingDiversityCount: int = Field(
        default=1, ge=1,
        description="Number of distinct crops grown"
    )

    # Crop health
    activeCropPercent: float = Field(..., ge=0, le=100)
    diseaseIncidentCount: int = Field(
        default=0, ge=0,
        description="Disease incidents in last 30 days"
    )

    # Soil management
    soilPH: Optional[float] = Field(default=7.0, ge=0, le=14)
    soilTestingDone: bool = Field(default=False)
    coverCroppingPracticed: bool = Field(default=False)


# ─── Irrigation efficiency lookup ─────────────────────────────────────────────

IRRIGATION_EFFICIENCY: dict[str, float] = {
    "Drip": 92,
    "Sprinkler": 78,
    "Furrow": 65,
    "Canal": 55,
    "Flood": 45,
    "Rain-fed": 40,
    "Borewell": 70,
    "Other": 60,
}

# Reference: benchmark litres/acre/day for average Indian farm (FAO)
BENCHMARK_WATER_USAGE = 5000  # litres/acre/day


# ─── Component scorers ────────────────────────────────────────────────────────

def _water_score(irrigation_type: str, usage: Optional[float]) -> tuple[float, list[str]]:
    tips = []
    eff = IRRIGATION_EFFICIENCY.get(irrigation_type, 60.0)
    base = eff  # 0–100

    if usage is not None and usage > 0:
        # Penalise if using more than benchmark
        if usage > BENCHMARK_WATER_USAGE:
            overuse_pct = ((usage - BENCHMARK_WATER_USAGE) / BENCHMARK_WATER_USAGE) * 100
            penalty = min(overuse_pct * 0.3, 30)
            base = max(base - penalty, 0)
            tips.append(
                f"ESTIMATED: Reducing water use to benchmark ({BENCHMARK_WATER_USAGE:,} L/acre/day) "
                f"could save ~{(usage - BENCHMARK_WATER_USAGE) * 365:,.0f} L/acre/year."
            )

    if eff < 70:
        tips.append(f"Switching from {irrigation_type} to Drip irrigation could improve efficiency by ~{92 - eff:.0f}%.")

    return round(base, 1), tips


def _resource_score(
    chemicals: bool, organic_pct: float, diversity: int
) -> tuple[float, list[str]]:
    tips = []
    score = 50.0  # baseline

    # Pesticide use
    if not chemicals:
        score += 20
    else:
        score -= 10
        tips.append("ESTIMATED: Reducing chemical pesticides could lower input costs by 10–20% (varies by crop).")

    # Organic fertiliser
    if organic_pct >= 50:
        score += 20
    elif organic_pct >= 25:
        score += 10
    elif organic_pct > 0:
        score += 5
    else:
        tips.append("Incorporating even 25% organic fertiliser improves soil biology and reduces input costs.")

    # Crop diversity
    if diversity >= 4:
        score += 15
    elif diversity >= 2:
        score += 8
    else:
        tips.append("Consider crop rotation or intercropping to reduce pest pressure and improve soil health.")

    return round(min(score, 100), 1), tips


def _crop_health_score(active_pct: float, disease_incidents: int) -> tuple[float, list[str]]:
    tips = []
    score = active_pct  # base from active crop coverage

    if disease_incidents > 3:
        score -= 20
        tips.append("High disease incidents detected. Strengthen IPM (Integrated Pest Management) practices.")
    elif disease_incidents > 0:
        score -= 8
        tips.append("Monitor for recurring disease patterns.")

    return round(max(score, 0), 1), tips


def _soil_score(ph: Optional[float], tested: bool, cover: bool) -> tuple[float, list[str]]:
    tips = []
    score = 40.0  # baseline

    # pH
    if ph is not None:
        if 6.0 <= ph <= 7.5:
            score += 30
        elif 5.5 <= ph < 6.0 or 7.5 < ph <= 8.0:
            score += 15
            tips.append("Soil pH slightly off optimal (6.0–7.5). Consider pH correction.")
        else:
            score += 0
            tips.append("Soil pH significantly off optimal range. Apply lime (for acidic) or sulphur (for alkaline).")

    # Soil testing
    if tested:
        score += 20
    else:
        tips.append("Conduct regular soil testing (Soil Health Card) to optimise inputs.")

    # Cover cropping
    if cover:
        score += 15
    else:
        tips.append("Cover cropping between seasons reduces erosion and improves organic matter.")

    return round(min(score, 100), 1), tips


# ─── Component weights ────────────────────────────────────────────────────────

WEIGHTS = {
    "waterEfficiency":      0.35,
    "resourceEfficiency":   0.25,
    "cropHealth":           0.25,
    "soilManagement":       0.15,
}


def _compute(data: SustainabilityRequest) -> dict:
    water_s, water_tips       = _water_score(data.irrigationType, data.waterUsageLitresPerAcre)
    resource_s, resource_tips = _resource_score(
        data.chemicalPesticidesUsed, data.organicFertilizerPercent, data.croppingDiversityCount
    )
    crop_s, crop_tips         = _crop_health_score(data.activeCropPercent, data.diseaseIncidentCount)
    soil_s, soil_tips         = _soil_score(data.soilPH, data.soilTestingDone, data.coverCroppingPracticed)

    components = {
        "waterEfficiency":    water_s,
        "resourceEfficiency": resource_s,
        "cropHealth":         crop_s,
        "soilManagement":     soil_s,
    }

    overall = round(sum(components[k] * WEIGHTS[k] for k in components), 1)

    if overall >= 75:
        grade = "Sustainable"
    elif overall >= 55:
        grade = "Moderately Sustainable"
    elif overall >= 35:
        grade = "Needs Improvement"
    else:
        grade = "Unsustainable Practices"

    all_tips = water_tips + resource_tips + crop_tips + soil_tips

    # ESTIMATED savings
    savings = _estimate_savings(data, water_s, resource_s)

    return {
        "overallScore": overall,
        "grade": grade,
        "components": {
            k: {
                "score": components[k],
                "weight": f"{int(WEIGHTS[k]*100)}%",
                "contribution": round(components[k] * WEIGHTS[k], 1),
            }
            for k in components
        },
        "weights": WEIGHTS,
        "improvementSuggestions": all_tips,
        "estimatedSavings": savings,
    }


def _estimate_savings(data: SustainabilityRequest, water_score: float, resource_score: float) -> dict:
    """
    ESTIMATED savings based on industry benchmarks.
    All figures are approximate and clearly labelled.
    """
    savings = {}

    # Water savings
    if data.irrigationType in ("Flood", "Furrow", "Canal") and data.waterUsageLitresPerAcre:
        drip_eff = IRRIGATION_EFFICIENCY["Drip"] / 100
        current_eff = IRRIGATION_EFFICIENCY.get(data.irrigationType, 50) / 100
        potential_pct = (drip_eff - current_eff) / current_eff * 100
        savings["waterSavings"] = {
            "value": f"~{potential_pct:.0f}%",
            "note": "ESTIMATED water saving by switching to drip irrigation (FAO benchmark)",
        }

    # Resource cost savings
    if data.chemicalPesticidesUsed:
        savings["pesticideCostSaving"] = {
            "value": "10–25%",
            "note": "ESTIMATED reduction in pesticide costs with integrated pest management (ICAR guideline)",
        }

    if data.organicFertilizerPercent < 25:
        savings["fertilizerCostSaving"] = {
            "value": "5–15%",
            "note": "ESTIMATED saving by incorporating organic matter (composting reduces input costs)",
        }

    return savings


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/score")
async def sustainability_score(data: SustainabilityRequest, user=Depends(get_current_user)):
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
        "disclaimer": "INDICATIVE Sustainability Score — ESTIMATED values based on FAO/ICAR benchmarks.",
    }
    ins = await db.sustainability_scores.insert_one(doc)

    return {
        "id": str(ins.inserted_id),
        "farmId": data.farmId,
        **result,
        "createdAt": doc["createdAt"],
        "disclaimer": doc["disclaimer"],
    }


@router.get("/{farm_id}/history")
async def sustainability_history(farm_id: str, user=Depends(get_current_user)):
    db = get_database()
    docs = await db.sustainability_scores.find(
        {"farmId": farm_id, "userId": str(user["_id"])}
    ).sort("createdAt", 1).to_list(50)

    return [
        {
            "id": str(d["_id"]),
            "overallScore": d["overallScore"],
            "grade": d["grade"],
            "createdAt": d["createdAt"],
        }
        for d in docs
    ]
