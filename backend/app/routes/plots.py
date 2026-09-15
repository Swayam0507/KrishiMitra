# ─── AgriFlow AI — Plot Routes ────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..schemas.plot import PlotCreate, PlotUpdate, PlotResponse
from ..dependencies import get_current_user

router = APIRouter()


def _serialize(plot: dict) -> PlotResponse:
    return PlotResponse(
        id=str(plot["_id"]),
        farmId=str(plot["farmId"]),
        plotName=plot["plotName"],
        area=plot["area"],
        soilType=plot.get("soilType"),
        soilPH=plot.get("soilPH"),
        soilMoisture=plot.get("soilMoisture"),
        waterAvailability=plot.get("waterAvailability"),
        currentCrop=plot.get("currentCrop"),
        cropStage=plot.get("cropStage"),
        createdAt=plot["createdAt"],
    )


def _oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


async def _verify_farm_owner(farm_id: str, user_id, db):
    """Ensure the given farm belongs to the current user."""
    farm = await db.farms.find_one({"_id": _oid(farm_id), "ownerId": user_id})
    if not farm:
        raise HTTPException(status_code=403, detail="Farm not found or access denied")
    return farm


@router.post("", response_model=PlotResponse, status_code=201)
async def create_plot(data: PlotCreate, user=Depends(get_current_user)):
    db = get_database()
    await _verify_farm_owner(data.farmId, user["_id"], db)

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.plots.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[PlotResponse])
async def list_plots(
    farmId: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    query: dict = {}
    if farmId:
        await _verify_farm_owner(farmId, user["_id"], db)
        query["farmId"] = farmId
    else:
        # Return plots for all farms owned by user
        user_farms = await db.farms.find({"ownerId": user["_id"]}, {"_id": 1}).to_list(500)
        farm_ids = [str(f["_id"]) for f in user_farms]
        query["farmId"] = {"$in": farm_ids}

    plots = await db.plots.find(query).sort("createdAt", -1).to_list(500)
    return [_serialize(p) for p in plots]


@router.get("/{plot_id}", response_model=PlotResponse)
async def get_plot(plot_id: str, user=Depends(get_current_user)):
    db = get_database()
    plot = await db.plots.find_one({"_id": _oid(plot_id)})
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    await _verify_farm_owner(plot["farmId"], user["_id"], db)
    return _serialize(plot)


@router.put("/{plot_id}", response_model=PlotResponse)
async def update_plot(plot_id: str, data: PlotUpdate, user=Depends(get_current_user)):
    db = get_database()
    plot = await db.plots.find_one({"_id": _oid(plot_id)})
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    await _verify_farm_owner(plot["farmId"], user["_id"], db)

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await db.plots.find_one_and_update(
        {"_id": _oid(plot_id)},
        {"$set": updates},
        return_document=True,
    )
    return _serialize(updated)


@router.delete("/{plot_id}", status_code=204)
async def delete_plot(plot_id: str, user=Depends(get_current_user)):
    db = get_database()
    plot = await db.plots.find_one({"_id": _oid(plot_id)})
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    await _verify_farm_owner(plot["farmId"], user["_id"], db)
    await db.plots.delete_one({"_id": _oid(plot_id)})
