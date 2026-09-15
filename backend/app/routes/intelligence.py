# ─── AgriFlow AI — Agricultural Intelligence Engine ───────────────────────────
"""
Central decision engine that aggregates data from all modules and produces
structured, prioritized recommendations.

Every recommendation contains:
  title, reason, priority, source, confidence (if applicable), recommendedAction

Priority levels: Critical > High > Medium > Low
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..dependencies import get_current_user
from ..services.irrigation_rules import rule_based_advice

router = APIRouter()


# ─── Recommendation builder ────────────────────────────────────────────────────

def _rec(title: str, reason: str, priority: str, source: str,
         action: str, confidence: Optional[float] = None) -> dict:
    return {
        "title": title,
        "reason": reason,
        "priority": priority,
        "source": source,
        "recommendedAction": action,
        "confidence": confidence,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


# ─── Individual analysis functions ────────────────────────────────────────────

async def _sensor_recommendations(farm_id: str, db) -> list[dict]:
    recs = []
    reading = await db.sensor_readings.find_one(
        {"farmId": farm_id}, sort=[("timestamp", -1)]
    )
    if not reading:
        return recs

    moisture = reading.get("soilMoisture", 50)
    temp = reading.get("temperature", 25)
    humidity = reading.get("humidity", 60)
    ph = reading.get("soilPH", 7.0)

    # Moisture
    if moisture < 25:
        recs.append(_rec(
            title="IRRIGATE — Critically Low Soil Moisture",
            reason=f"Soil moisture is {moisture:.1f}% — well below safe minimum (30%). Crop stress likely.",
            priority="Critical",
            source="IoT Sensor (SIMULATED)",
            action="Apply full irrigation cycle immediately.",
        ))
    elif moisture < 40:
        recs.append(_rec(
            title="IRRIGATE — Low Soil Moisture",
            reason=f"Soil moisture is {moisture:.1f}% — below recommended range (40–70%).",
            priority="High",
            source="IoT Sensor (SIMULATED)",
            action="Schedule irrigation within the next 6 hours.",
        ))
    elif moisture > 85:
        recs.append(_rec(
            title="REDUCE IRRIGATION — High Soil Moisture",
            reason=f"Soil moisture is {moisture:.1f}% — above optimal range. Risk of waterlogging and root disease.",
            priority="High",
            source="IoT Sensor (SIMULATED)",
            action="Skip next irrigation cycle. Check field drainage.",
        ))

    # Temperature
    if temp > 42:
        recs.append(_rec(
            title="HEAT STRESS ALERT",
            reason=f"Temperature {temp:.1f}°C is dangerously high for most crops.",
            priority="Critical",
            source="IoT Sensor (SIMULATED)",
            action="Provide shade netting for sensitive crops. Increase irrigation frequency.",
        ))
    elif temp < 5:
        recs.append(_rec(
            title="COLD STRESS ALERT",
            reason=f"Temperature {temp:.1f}°C — frost risk for sensitive crops.",
            priority="High",
            source="IoT Sensor (SIMULATED)",
            action="Cover seedlings. Delay transplanting operations.",
        ))

    # Humidity — disease risk
    if humidity > 85:
        recs.append(_rec(
            title="HIGH DISEASE RISK — High Humidity",
            reason=f"Humidity {humidity:.1f}% creates ideal conditions for fungal diseases.",
            priority="High",
            source="IoT Sensor (SIMULATED)",
            action="Inspect crops for early disease signs. Ensure adequate plant spacing.",
        ))

    # pH
    if ph < 5.5:
        recs.append(_rec(
            title="SOIL pH TOO ACIDIC",
            reason=f"Soil pH {ph:.1f} is below optimal range (6.0–7.5). Nutrient availability is reduced.",
            priority="Medium",
            source="IoT Sensor (SIMULATED)",
            action="Apply agricultural lime to raise soil pH.",
        ))
    elif ph > 8.0:
        recs.append(_rec(
            title="SOIL pH TOO ALKALINE",
            reason=f"Soil pH {ph:.1f} is above optimal range. Iron and manganese deficiencies possible.",
            priority="Medium",
            source="IoT Sensor (SIMULATED)",
            action="Apply elemental sulphur or gypsum to lower pH.",
        ))

    return recs


async def _inventory_recommendations(farm_id: str, db) -> list[dict]:
    recs = []
    items = await db.inventory.find({"farmId": farm_id}).to_list(200)

    for item in items:
        qty = item.get("quantity", 0)
        min_level = item.get("minimumLevel", 0)
        if qty <= 0:
            recs.append(_rec(
                title=f"OUT OF STOCK — {item['name']}",
                reason=f"{item['name']} ({item['category']}) is completely out of stock.",
                priority="High",
                source="Inventory",
                action=f"Restock {item['name']} immediately.",
            ))
        elif qty <= min_level:
            recs.append(_rec(
                title=f"LOW STOCK — {item['name']}",
                reason=f"{item['name']} quantity ({qty:.1f} {item.get('unit','')}) is at or below minimum level ({min_level:.1f}).",
                priority="Medium",
                source="Inventory",
                action=f"Order {item['name']} soon to avoid stockout.",
            ))

    return recs


async def _activity_recommendations(farm_id: str, db) -> list[dict]:
    recs = []
    now = datetime.now(timezone.utc)
    overdue_activities = await db.activities.find({
        "farmId": farm_id,
        "status": "Pending",
        "date": {"$lt": now},
    }).to_list(10)

    for act in overdue_activities:
        recs.append(_rec(
            title=f"OVERDUE ACTIVITY — {act['activityType']}",
            reason=f"{act['activityType']} was scheduled for {act['date'].strftime('%d %b %Y')} and is still pending.",
            priority="Medium",
            source="Activity Planner",
            action=f"Complete the {act['activityType']} activity or reschedule it.",
        ))

    return recs


async def _disease_risk_recommendations(farm_id: str, user_id: str, db) -> list[dict]:
    recs = []
    latest_risk = await db.disease_risk.find_one(
        {"farmId": farm_id, "userId": user_id},
        sort=[("createdAt", -1)],
    )
    if latest_risk and latest_risk.get("riskScore", 0) >= 66:
        recs.append(_rec(
            title="HIGH DISEASE RISK DETECTED",
            reason=(
                f"Disease risk score is {latest_risk['riskScore']}/100 ({latest_risk['riskBand']}). "
                f"Key factors: {', '.join(latest_risk.get('factors', [])[:2])}"
            ),
            priority="High",
            source="Disease Risk Engine",
            action="Inspect crops immediately. Consider preventive fungicide application.",
        ))
    return recs


async def _latest_disease_prediction_rec(user_id: str, db) -> list[dict]:
    recs = []
    pred = await db.disease_predictions.find_one(
        {"userId": user_id, "disease": {"$ne": None}},
        sort=[("createdAt", -1)],
    )
    if pred and pred.get("confidence", 0) and pred["confidence"] > 0.7:
        recs.append(_rec(
            title=f"DISEASE DETECTED — {pred['disease']}",
            reason=f"Recent image analysis detected {pred['disease']} with {pred['confidence']*100:.0f}% confidence.",
            priority="Critical" if pred.get("risk") == "HIGH" else "High",
            source="Disease AI (CV Model)",
            confidence=pred["confidence"],
            action="; ".join(pred.get("recommendations", ["Consult an agronomist."])[:2]),
        ))
    return recs


# ─── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("/recommendations/{farm_id}")
async def get_recommendations(
    farm_id: str,
    user=Depends(get_current_user),
):
    """
    Run the agricultural intelligence engine for a farm.
    Returns a prioritized list of recommendations from all data sources.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(farm_id), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Gather recommendations from all sources
    all_recs = []
    all_recs += await _sensor_recommendations(farm_id, db)
    all_recs += await _inventory_recommendations(farm_id, db)
    all_recs += await _activity_recommendations(farm_id, db)
    all_recs += await _disease_risk_recommendations(farm_id, str(user["_id"]), db)
    all_recs += await _latest_disease_prediction_rec(str(user["_id"]), db)

    # Sort by priority
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    all_recs.sort(key=lambda r: priority_order.get(r["priority"], 4))

    # Save to DB
    doc = {
        "farmId": farm_id,
        "userId": str(user["_id"]),
        "recommendations": all_recs,
        "totalCount": len(all_recs),
        "criticalCount": sum(1 for r in all_recs if r["priority"] == "Critical"),
        "highCount": sum(1 for r in all_recs if r["priority"] == "High"),
        "generatedAt": datetime.now(timezone.utc),
    }
    await db.intelligence_reports.insert_one(doc)

    return {
        "farmId": farm_id,
        "farmName": farm["farmName"],
        "totalRecommendations": len(all_recs),
        "criticalCount": doc["criticalCount"],
        "highCount": doc["highCount"],
        "recommendations": all_recs,
        "generatedAt": doc["generatedAt"],
    }
