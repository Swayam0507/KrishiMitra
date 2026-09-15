# ─── AgriFlow AI — IoT Sensor Simulation (SIH Bonus Module F) ────────────────
"""
Simulates realistic sensor readings for:
  - Soil Moisture (%)
  - Temperature (°C)
  - Humidity (%)
  - Soil pH

Architecture:
  Simulator → FastAPI → MongoDB → Dashboard

All readings are clearly labelled SIMULATED SENSOR DATA.
Readings use realistic variation around a baseline with small random drift.
"""
import asyncio
import random
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()

# ─── Simulation state (in-memory per process) ─────────────────────────────────
# Maps farmId → bool (is simulation running)
_simulation_running: dict[str, bool] = {}


# ─── Sensor baseline profiles per soil type ───────────────────────────────────
SOIL_PROFILES: dict[str, dict] = {
    "Loamy":         {"moisture": 55, "ph": 6.8, "ph_drift": 0.05},
    "Clay":          {"moisture": 65, "ph": 7.2, "ph_drift": 0.04},
    "Sandy":         {"moisture": 30, "ph": 6.2, "ph_drift": 0.06},
    "Silty":         {"moisture": 60, "ph": 6.9, "ph_drift": 0.04},
    "Peaty":         {"moisture": 70, "ph": 5.5, "ph_drift": 0.08},
    "Chalky":        {"moisture": 35, "ph": 7.8, "ph_drift": 0.05},
    "Black Cotton":  {"moisture": 62, "ph": 7.5, "ph_drift": 0.04},
    "Red Laterite":  {"moisture": 40, "ph": 6.0, "ph_drift": 0.06},
}
DEFAULT_PROFILE = {"moisture": 50, "ph": 7.0, "ph_drift": 0.05}


def _generate_reading(farm: dict, previous: Optional[dict] = None) -> dict:
    """
    Generate a single realistic sensor reading.
    Uses small random drift from previous reading for continuity.
    Values are constrained to realistic agronomic ranges.
    """
    soil_type = farm.get("soilType", "Loamy")
    profile = SOIL_PROFILES.get(soil_type, DEFAULT_PROFILE)

    if previous:
        # Drift from previous: small random walk
        moisture    = _drift(previous["soilMoisture"], profile["moisture"],    min_v=10,  max_v=95,  step=1.5)
        temperature = _drift(previous["temperature"],  28.0,                   min_v=15,  max_v=45,  step=0.8)
        humidity    = _drift(previous["humidity"],     60.0,                   min_v=20,  max_v=98,  step=1.2)
        ph          = _drift(previous["soilPH"],       profile["ph"],          min_v=4.5, max_v=8.5, step=profile["ph_drift"])
    else:
        # First reading: baseline + small noise
        moisture    = round(profile["moisture"]     + random.uniform(-5, 5), 2)
        temperature = round(28.0                    + random.uniform(-3, 3), 2)
        humidity    = round(60.0                    + random.uniform(-10, 10), 2)
        ph          = round(profile["ph"]           + random.uniform(-0.1, 0.1), 2)

    return {
        "farmId":        str(farm["_id"]),
        "soilType":      soil_type,
        "soilMoisture":  round(moisture, 2),
        "temperature":   round(temperature, 2),
        "humidity":      round(humidity, 2),
        "soilPH":        round(ph, 2),
        "dataSource":    "SIMULATED SENSOR",
        "timestamp":     datetime.now(timezone.utc),
    }


def _drift(current: float, target: float, min_v: float, max_v: float, step: float) -> float:
    """Random walk biased toward the target baseline."""
    direction = 1 if target > current else -1
    noise = random.uniform(-step, step)
    bias  = direction * random.uniform(0, step * 0.3)
    return max(min_v, min(max_v, current + noise + bias))


# ─── Background simulation task ───────────────────────────────────────────────

async def _run_simulation(farm_id: str, interval_seconds: int = 30):
    """
    Background task: generate readings every `interval_seconds`.
    Stops when _simulation_running[farm_id] is set to False.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": __import__("bson").ObjectId(farm_id)})
    if not farm:
        _simulation_running.pop(farm_id, None)
        return

    previous = None
    while _simulation_running.get(farm_id, False):
        reading = _generate_reading(farm, previous)
        await db.sensor_readings.insert_one(reading)
        previous = reading
        await asyncio.sleep(interval_seconds)

    _simulation_running.pop(farm_id, None)


# ─── Request schemas ──────────────────────────────────────────────────────────

class StartSimulationRequest(BaseModel):
    farmId: str
    intervalSeconds: int = Field(default=30, ge=5, le=300)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_single_reading(
    farmId: str = Query(...),
    user=Depends(get_current_user),
):
    """Generate and store a single sensor reading on demand."""
    db = get_database()
    from bson import ObjectId
    farm = await db.farms.find_one({"_id": ObjectId(farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Get previous reading for drift continuity
    prev = await db.sensor_readings.find_one(
        {"farmId": farmId}, sort=[("timestamp", -1)]
    )
    reading = _generate_reading(farm, prev)
    result = await db.sensor_readings.insert_one(reading)
    reading["_id"] = result.inserted_id

    return {
        "id": str(reading["_id"]),
        **{k: v for k, v in reading.items() if k != "_id"},
        "note": "SIMULATED SENSOR DATA — not from a physical device",
    }


@router.post("/simulate/start")
async def start_simulation(
    data: StartSimulationRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """Start continuous sensor simulation for a farm."""
    db = get_database()
    from bson import ObjectId
    farm = await db.farms.find_one({"_id": ObjectId(data.farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    if _simulation_running.get(data.farmId):
        return {"message": "Simulation already running", "farmId": data.farmId, "status": "running"}

    _simulation_running[data.farmId] = True
    background_tasks.add_task(_run_simulation, data.farmId, data.intervalSeconds)

    return {
        "message": "Simulation started",
        "farmId": data.farmId,
        "intervalSeconds": data.intervalSeconds,
        "status": "running",
        "note": "SIMULATED SENSOR DATA — readings generated every interval",
    }


@router.post("/simulate/stop")
async def stop_simulation(farmId: str = Query(...), user=Depends(get_current_user)):
    """Stop the running simulation for a farm."""
    if not _simulation_running.get(farmId):
        return {"message": "No simulation running for this farm", "farmId": farmId, "status": "stopped"}

    _simulation_running[farmId] = False
    return {"message": "Simulation stopped", "farmId": farmId, "status": "stopped"}


@router.get("/status")
async def simulation_status(farmId: str = Query(...), user=Depends(get_current_user)):
    """Check if simulation is running for a farm."""
    return {
        "farmId": farmId,
        "status": "running" if _simulation_running.get(farmId) else "stopped",
    }


@router.get("/readings")
async def get_readings(
    farmId: str = Query(...),
    limit: int = Query(default=50, le=500),
    user=Depends(get_current_user),
):
    """Return recent sensor readings for a farm."""
    db = get_database()
    from bson import ObjectId
    farm = await db.farms.find_one({"_id": ObjectId(farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    docs = await db.sensor_readings.find(
        {"farmId": farmId}
    ).sort("timestamp", -1).limit(limit).to_list(limit)

    return [
        {
            "id": str(d["_id"]),
            "soilMoisture": d["soilMoisture"],
            "temperature": d["temperature"],
            "humidity": d["humidity"],
            "soilPH": d["soilPH"],
            "soilType": d.get("soilType"),
            "dataSource": d.get("dataSource", "SIMULATED SENSOR"),
            "timestamp": d["timestamp"],
        }
        for d in reversed(docs)   # ascending for charts
    ]


@router.get("/latest")
async def latest_reading(farmId: str = Query(...), user=Depends(get_current_user)):
    """Return the most recent sensor reading for a farm."""
    db = get_database()
    from bson import ObjectId
    farm = await db.farms.find_one({"_id": ObjectId(farmId), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    doc = await db.sensor_readings.find_one(
        {"farmId": farmId}, sort=[("timestamp", -1)]
    )
    if not doc:
        return {"message": "No readings yet. Use /sensors/generate or /sensors/simulate/start"}

    return {
        "id": str(doc["_id"]),
        "soilMoisture": doc["soilMoisture"],
        "temperature": doc["temperature"],
        "humidity": doc["humidity"],
        "soilPH": doc["soilPH"],
        "soilType": doc.get("soilType"),
        "dataSource": doc.get("dataSource", "SIMULATED SENSOR"),
        "timestamp": doc["timestamp"],
        "note": "SIMULATED SENSOR DATA",
    }
