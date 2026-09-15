# ─── AgriFlow AI — Farm Routes ────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_database
from ..schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from ..dependencies import get_current_user

router = APIRouter()


def _serialize(farm: dict) -> FarmResponse:
    return FarmResponse(
        id=str(farm["_id"]),
        farmName=farm["farmName"],
        location=farm["location"],
        area=farm["area"],
        areaUnit=farm.get("areaUnit", "acres"),
        soilType=farm.get("soilType", "Loamy"),
        irrigationType=farm.get("irrigationType", "Drip"),
        latitude=farm.get("latitude"),
        longitude=farm.get("longitude"),
        ownerId=str(farm["ownerId"]),
        createdAt=farm["createdAt"],
    )


def _oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


@router.post("", response_model=FarmResponse, status_code=201)
async def create_farm(data: FarmCreate, user=Depends(get_current_user)):
    db = get_database()
    doc = {**data.model_dump(), "ownerId": user["_id"], "createdAt": datetime.now(timezone.utc)}
    result = await db.farms.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[FarmResponse])
async def list_farms(user=Depends(get_current_user)):
    db = get_database()
    farms = await db.farms.find({"ownerId": user["_id"]}).sort("createdAt", -1).to_list(200)
    return [_serialize(f) for f in farms]


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str, user=Depends(get_current_user)):
    db = get_database()
    farm = await db.farms.find_one({"_id": _oid(farm_id), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return _serialize(farm)


@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(farm_id: str, data: FarmUpdate, user=Depends(get_current_user)):
    db = get_database()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    farm = await db.farms.find_one_and_update(
        {"_id": _oid(farm_id), "ownerId": user["_id"]},
        {"$set": updates},
        return_document=True,
    )
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return _serialize(farm)


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(farm_id: str, user=Depends(get_current_user)):
    db = get_database()
    result = await db.farms.delete_one({"_id": _oid(farm_id), "ownerId": user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.get("/{farm_id}/stats")
async def farm_stats(farm_id: str, user=Depends(get_current_user)):
    """Return quick aggregate stats for a farm."""
    db = get_database()
    oid = _oid(farm_id)
    farm = await db.farms.find_one({"_id": oid, "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    total_plots = await db.plots.count_documents({"farmId": farm_id})
    active_crops = await db.crops.count_documents({"status": "Active"})
    pending_activities = await db.activities.count_documents({"farmId": farm_id, "status": "Pending"})
    total_workers = await db.workers.count_documents({"farmId": farm_id})

    return {
        "totalPlots": total_plots,
        "activeCrops": active_crops,
        "pendingActivities": pending_activities,
        "totalWorkers": total_workers,
    }
