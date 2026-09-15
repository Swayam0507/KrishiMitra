# ─── AgriFlow AI — Alert & Notification Center (Phase 32) ────────────────────
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()

ALERT_TYPES = [
    "Disease", "Irrigation", "Weather", "Inventory",
    "Sensor", "Crop", "Activity", "FarmHealth", "Sustainability", "General",
]
PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]


class AlertCreate(BaseModel):
    type: str = Field(..., description=f"One of: {ALERT_TYPES}")
    title: str = Field(..., min_length=2, max_length=200)
    message: str = Field(..., min_length=2, max_length=1000)
    priority: str = Field(default="Medium")
    farmId: Optional[str] = None
    plotId: Optional[str] = None


def _serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "type": doc["type"],
        "title": doc["title"],
        "message": doc["message"],
        "priority": doc.get("priority", "Medium"),
        "farmId": doc.get("farmId"),
        "plotId": doc.get("plotId"),
        "read": doc.get("read", False),
        "createdAt": doc["createdAt"],
    }


def _priority_sort(priority: str) -> int:
    return {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(priority, 4)


@router.post("", status_code=201)
async def create_alert(data: AlertCreate, user=Depends(get_current_user)):
    """Create a manual alert."""
    db = get_database()
    doc = {
        "userId": str(user["_id"]),
        **data.model_dump(),
        "read": False,
        "createdAt": datetime.now(timezone.utc),
    }
    result = await db.alerts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("")
async def list_alerts(
    type: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    read: Optional[bool] = Query(default=None),
    farmId: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
    user=Depends(get_current_user),
):
    """Return alerts for the current user with optional filters."""
    db = get_database()
    query: dict = {"userId": str(user["_id"])}

    if type:
        query["type"] = type
    if priority:
        query["priority"] = priority
    if read is not None:
        query["read"] = read
    if farmId:
        query["farmId"] = farmId

    docs = await db.alerts.find(query).sort("createdAt", -1).limit(limit).to_list(limit)
    alerts = [_serialize(d) for d in docs]
    alerts.sort(key=lambda a: (_priority_sort(a["priority"]), a["read"]))
    return alerts


@router.get("/summary")
async def alert_summary(user=Depends(get_current_user)):
    """Return unread alert counts by priority."""
    db = get_database()
    docs = await db.alerts.find(
        {"userId": str(user["_id"]), "read": False}
    ).to_list(1000)

    counts: dict = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "total": 0}
    for d in docs:
        p = d.get("priority", "Medium")
        if p in counts:
            counts[p] += 1
        counts["total"] += 1

    return counts


@router.patch("/{alert_id}/read")
async def mark_read(alert_id: str, user=Depends(get_current_user)):
    """Mark an alert as read."""
    db = get_database()
    try:
        result = await db.alerts.find_one_and_update(
            {"_id": ObjectId(alert_id), "userId": str(user["_id"])},
            {"$set": {"read": True}},
            return_document=True,
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid alert ID")

    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _serialize(result)


@router.patch("/mark-all-read")
async def mark_all_read(user=Depends(get_current_user)):
    """Mark all unread alerts as read."""
    db = get_database()
    result = await db.alerts.update_many(
        {"userId": str(user["_id"]), "read": False},
        {"$set": {"read": True}},
    )
    return {"message": f"Marked {result.modified_count} alerts as read"}


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: str, user=Depends(get_current_user)):
    """Delete an alert."""
    db = get_database()
    try:
        result = await db.alerts.delete_one(
            {"_id": ObjectId(alert_id), "userId": str(user["_id"])}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid alert ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/generate/{farm_id}")
async def auto_generate_alerts(farm_id: str, user=Depends(get_current_user)):
    """
    Auto-generate alerts for a farm based on current conditions:
    - Sensor anomalies, low inventory, overdue activities, high risk.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(farm_id), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    generated = []

    # Inventory alerts
    items = await db.inventory.find({"farmId": farm_id}).to_list(100)
    for item in items:
        qty = item.get("quantity", 0)
        min_level = item.get("minimumLevel", 0)
        if qty <= 0:
            alert_doc = {
                "userId": str(user["_id"]),
                "type": "Inventory",
                "title": f"Out of Stock: {item['name']}",
                "message": f"{item['name']} is completely out of stock. Restock immediately.",
                "priority": "High",
                "farmId": farm_id,
                "read": False,
                "createdAt": datetime.now(timezone.utc),
            }
            await db.alerts.insert_one(alert_doc)
            generated.append(alert_doc["title"])
        elif qty <= min_level:
            alert_doc = {
                "userId": str(user["_id"]),
                "type": "Inventory",
                "title": f"Low Stock: {item['name']}",
                "message": f"{item['name']}: {qty:.1f} {item.get('unit','')} remaining (minimum: {min_level:.1f}).",
                "priority": "Medium",
                "farmId": farm_id,
                "read": False,
                "createdAt": datetime.now(timezone.utc),
            }
            await db.alerts.insert_one(alert_doc)
            generated.append(alert_doc["title"])

    # Disease risk alert
    risk = await db.disease_risk.find_one(
        {"farmId": farm_id, "userId": str(user["_id"])},
        sort=[("createdAt", -1)],
    )
    if risk and risk.get("riskScore", 0) >= 66:
        alert_doc = {
            "userId": str(user["_id"]),
            "type": "Disease",
            "title": f"High Disease Risk — {risk['riskScore']}/100",
            "message": f"Disease risk score is {risk['riskScore']}/100 ({risk['riskBand']}). Immediate crop inspection recommended.",
            "priority": "Critical",
            "farmId": farm_id,
            "read": False,
            "createdAt": datetime.now(timezone.utc),
        }
        await db.alerts.insert_one(alert_doc)
        generated.append(alert_doc["title"])

    # Sensor: critical moisture
    sensor = await db.sensor_readings.find_one(
        {"farmId": farm_id}, sort=[("timestamp", -1)]
    )
    if sensor:
        m = sensor.get("soilMoisture", 50)
        if m < 20:
            alert_doc = {
                "userId": str(user["_id"]),
                "type": "Sensor",
                "title": f"Critical Soil Moisture — {m:.1f}%",
                "message": f"Soil moisture is {m:.1f}% (SIMULATED). Immediate irrigation required.",
                "priority": "Critical",
                "farmId": farm_id,
                "read": False,
                "createdAt": datetime.now(timezone.utc),
            }
            await db.alerts.insert_one(alert_doc)
            generated.append(alert_doc["title"])

    return {
        "message": f"Generated {len(generated)} alerts",
        "alerts": generated,
        "farmId": farm_id,
    }
