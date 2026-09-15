# ─── AgriFlow AI — Agentic Farm Advisor (Bonus Module G) ─────────────────────
"""
Lightweight deterministic agent workflow.
OBSERVE → ANALYZE → CHECK WEATHER → CHECK SENSOR → ASSESS RISK → DECIDE → RECOMMEND → MONITOR

All actions are advisory only. No autonomous actions are taken.
Decision history is stored in MongoDB.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..dependencies import get_current_user
from ..services.irrigation_rules import rule_based_advice

router = APIRouter()


class AgentRunRequest(BaseModel):
    farmId: str
    plotId: Optional[str] = None
    cropType: Optional[str] = None
    cropStage: Optional[str] = None


async def _step_observe(farm_id: str, db) -> dict:
    """OBSERVE: Collect raw data from all farm sources."""
    farm = await db.farms.find_one({"_id": ObjectId(farm_id)})
    plots = await db.plots.find({"farmId": farm_id}).to_list(20)
    crops = await db.crops.find({"status": "Active"}).to_list(20)
    sensor = await db.sensor_readings.find_one(
        {"farmId": farm_id}, sort=[("timestamp", -1)]
    )
    activities = await db.activities.find(
        {"farmId": farm_id, "status": "Pending"}
    ).limit(5).to_list(5)

    return {
        "step": "OBSERVE",
        "farmName": farm.get("farmName") if farm else "Unknown",
        "totalPlots": len(plots),
        "activeCrops": len(crops),
        "hasSensorData": sensor is not None,
        "pendingActivities": len(activities),
        "sensorSnapshot": {
            "soilMoisture": sensor.get("soilMoisture") if sensor else None,
            "temperature": sensor.get("temperature") if sensor else None,
            "humidity": sensor.get("humidity") if sensor else None,
            "soilPH": sensor.get("soilPH") if sensor else None,
            "timestamp": sensor.get("timestamp") if sensor else None,
        } if sensor else None,
    }


async def _step_analyze(farm_id: str, db, observed: dict) -> dict:
    """ANALYZE: Evaluate observed data for critical conditions."""
    issues: list[str] = []
    opportunities: list[str] = []

    sensor = observed.get("sensorSnapshot")
    if sensor:
        m = sensor.get("soilMoisture")
        if m is not None:
            if m < 25:
                issues.append(f"Critical soil moisture ({m:.1f}%) — immediate irrigation needed")
            elif m < 40:
                issues.append(f"Low soil moisture ({m:.1f}%) — monitor closely")
            elif m > 85:
                issues.append(f"High soil moisture ({m:.1f}%) — waterlogging risk")

        t = sensor.get("temperature")
        if t is not None and t > 40:
            issues.append(f"High temperature ({t:.1f}°C) — heat stress possible")

        h = sensor.get("humidity")
        if h is not None and h > 85:
            issues.append(f"High humidity ({h:.1f}%) — disease risk elevated")

        ph = sensor.get("soilPH")
        if ph is not None and (ph < 5.5 or ph > 8.0):
            issues.append(f"Soil pH {ph:.1f} outside optimal range (6.0–7.5)")

    if observed["pendingActivities"] > 3:
        issues.append(f"{observed['pendingActivities']} pending activities — farm operations may be behind schedule")

    if not issues:
        opportunities.append("Farm conditions appear normal — good time for routine monitoring.")

    return {
        "step": "ANALYZE",
        "issuesFound": len(issues),
        "issues": issues,
        "opportunities": opportunities,
    }


async def _step_check_weather(farm_id: str, db) -> dict:
    """CHECK WEATHER: Look for recent weather recommendations stored in DB."""
    # In Phase 20 we store weather data; here we check the most recent
    # In a production system this would call the weather service
    return {
        "step": "CHECK_WEATHER",
        "weatherAvailable": False,
        "note": "Connect OpenWeatherMap API key in .env for live weather. Skipped for now.",
        "rainProbability": None,
    }


async def _step_check_sensor(farm_id: str, db) -> dict:
    """CHECK SENSOR: Retrieve latest sensor reading for decision input."""
    sensor = await db.sensor_readings.find_one(
        {"farmId": farm_id}, sort=[("timestamp", -1)]
    )
    if not sensor:
        return {"step": "CHECK_SENSOR", "available": False, "data": None}

    return {
        "step": "CHECK_SENSOR",
        "available": True,
        "dataSource": "SIMULATED SENSOR",
        "data": {
            "soilMoisture": sensor.get("soilMoisture"),
            "temperature": sensor.get("temperature"),
            "humidity": sensor.get("humidity"),
            "soilPH": sensor.get("soilPH"),
            "timestamp": sensor.get("timestamp"),
        },
    }


async def _step_assess_risk(farm_id: str, user_id: str, crop_type: Optional[str], db) -> dict:
    """ASSESS RISK: Retrieve latest disease risk assessment."""
    risk_doc = await db.disease_risk.find_one(
        {"farmId": farm_id, "userId": user_id}, sort=[("createdAt", -1)]
    )
    if risk_doc:
        return {
            "step": "ASSESS_RISK",
            "riskScore": risk_doc.get("riskScore"),
            "riskBand": risk_doc.get("riskBand"),
            "topFactors": risk_doc.get("factors", [])[:3],
        }
    return {
        "step": "ASSESS_RISK",
        "riskScore": None,
        "riskBand": "Unknown",
        "topFactors": [],
        "note": "No risk assessment found. Run /api/risk/assess first.",
    }


def _step_decide(sensor_data: Optional[dict], risk_band: str, crop_type: Optional[str],
                 crop_stage: Optional[str], rain_prob: Optional[float]) -> dict:
    """DECIDE: Apply irrigation rules and risk context to make a decision."""
    if sensor_data and sensor_data.get("data"):
        sd = sensor_data["data"]
        advice = rule_based_advice({
            "soilMoisture": sd.get("soilMoisture", 50),
            "temperature": sd.get("temperature", 25),
            "humidity": sd.get("humidity", 60),
            "rainProbability": rain_prob or 0,
            "cropType": crop_type,
            "growthStage": crop_stage,
            "recentRainfall": 0,
        })
        irrigation_decision = advice.get("decision", "WAIT")
        irrigation_reason = advice.get("reason", "Insufficient data.")
    else:
        irrigation_decision = "WAIT"
        irrigation_reason = "No sensor data available — cannot make precise irrigation decision."

    # Override based on risk
    alerts = []
    if risk_band == "High":
        alerts.append("High disease risk — avoid overhead irrigation to reduce leaf wetness.")

    return {
        "step": "DECIDE",
        "irrigationDecision": irrigation_decision,
        "irrigationReason": irrigation_reason,
        "diseaseRisk": risk_band,
        "alerts": alerts,
    }


def _step_recommend(analysis: dict, decision: dict, crop_type: Optional[str],
                    crop_stage: Optional[str]) -> dict:
    """RECOMMEND: Produce final structured recommendations."""
    actions = []

    irrigation_action = decision.get("irrigationDecision", "WAIT")
    if irrigation_action == "IRRIGATE":
        actions.append({
            "type": "Irrigation",
            "action": decision["irrigationReason"],
            "urgency": "Now",
        })
    elif irrigation_action == "REDUCE IRRIGATION":
        actions.append({
            "type": "Irrigation",
            "action": decision["irrigationReason"],
            "urgency": "Next cycle",
        })
    else:
        actions.append({
            "type": "Irrigation",
            "action": decision["irrigationReason"],
            "urgency": "Scheduled",
        })

    for issue in analysis.get("issues", []):
        actions.append({"type": "Alert", "action": issue, "urgency": "Monitor"})

    return {
        "step": "RECOMMEND",
        "recommendedActions": actions,
        "nextCheckIn": "6 hours" if irrigation_action == "WAIT" else "2 hours",
        "summary": (
            f"Irrigation: {irrigation_action} | "
            f"Disease Risk: {decision.get('diseaseRisk', 'Unknown')} | "
            f"Issues: {analysis.get('issuesFound', 0)}"
        ),
    }


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/run")
async def run_agent(data: AgentRunRequest, user=Depends(get_current_user)):
    """
    Execute the full agent workflow for a farm.
    Returns a complete step-by-step decision trace.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(data.farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Execute agent steps sequentially
    observed      = await _step_observe(data.farmId, db)
    analyzed      = await _step_analyze(data.farmId, db, observed)
    weather_check = await _step_check_weather(data.farmId, db)
    sensor_check  = await _step_check_sensor(data.farmId, db)
    risk_check    = await _step_assess_risk(data.farmId, str(user["_id"]), data.cropType, db)
    decision      = _step_decide(
        sensor_check,
        risk_check.get("riskBand", "Unknown"),
        data.cropType,
        data.cropStage,
        weather_check.get("rainProbability"),
    )
    recommendation = _step_recommend(analyzed, decision, data.cropType, data.cropStage)

    result = {
        "farmId": data.farmId,
        "farmName": farm["farmName"],
        "agentVersion": "v1.0 — Deterministic Advisory Agent",
        "disclaimer": "All recommendations are advisory only. No autonomous actions are taken.",
        "workflow": [observed, analyzed, weather_check, sensor_check, risk_check, decision, recommendation],
        "finalDecision": decision.get("irrigationDecision"),
        "summary": recommendation.get("summary"),
        "nextCheckIn": recommendation.get("nextCheckIn"),
        "executedAt": datetime.now(timezone.utc),
    }

    # Persist
    await db.agent_decisions.insert_one({
        "userId": str(user["_id"]),
        **result,
    })

    return result


@router.get("/history/{farm_id}")
async def agent_history(
    farm_id: str,
    limit: int = Query(default=20, le=100),
    user=Depends(get_current_user),
):
    """Return the history of agent decisions for a farm."""
    db = get_database()
    docs = await db.agent_decisions.find(
        {"farmId": farm_id, "userId": str(user["_id"])}
    ).sort("executedAt", -1).limit(limit).to_list(limit)

    return [
        {
            "id": str(d["_id"]),
            "finalDecision": d.get("finalDecision"),
            "summary": d.get("summary"),
            "nextCheckIn": d.get("nextCheckIn"),
            "executedAt": d.get("executedAt"),
        }
        for d in docs
    ]
