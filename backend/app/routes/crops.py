# ─── AgriFlow AI — Crop Routes ────────────────────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..schemas.crop import CropCreate, CropUpdate, CropResponse, VALID_STAGES, VALID_STATUS
from ..dependencies import get_current_user

router = APIRouter()


def _serialize(crop: dict) -> CropResponse:
    return CropResponse(
        id=str(crop["_id"]),
        plotId=str(crop["plotId"]),
        cropName=crop["cropName"],
        variety=crop.get("variety"),
        plantingDate=crop["plantingDate"],
        expectedHarvestDate=crop.get("expectedHarvestDate"),
        currentStage=crop.get("currentStage", "Seed"),
        seedSource=crop.get("seedSource"),
        area=crop["area"],
        status=crop.get("status", "Active"),
        createdAt=crop["createdAt"],
    )


def _oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


async def _verify_plot_owner(plot_id: str, user_id, db):
    plot = await db.plots.find_one({"_id": _oid(plot_id)})
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")
    farm = await db.farms.find_one({"_id": _oid(plot["farmId"]), "ownerId": user_id})
    if not farm:
        raise HTTPException(status_code=403, detail="Access denied")
    return plot


@router.post("", response_model=CropResponse, status_code=201)
async def create_crop(data: CropCreate, user=Depends(get_current_user)):
    db = get_database()
    await _verify_plot_owner(data.plotId, user["_id"], db)

    if data.currentStage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of {VALID_STAGES}")
    if data.status not in VALID_STATUS:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_STATUS}")

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.crops.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[CropResponse])
async def list_crops(
    plotId: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    query: dict = {}

    if plotId:
        await _verify_plot_owner(plotId, user["_id"], db)
        query["plotId"] = plotId
    else:
        # Fetch all crops belonging to user's plots
        user_farms = await db.farms.find({"ownerId": user["_id"]}, {"_id": 1}).to_list(500)
        farm_ids = [str(f["_id"]) for f in user_farms]
        user_plots = await db.plots.find({"farmId": {"$in": farm_ids}}, {"_id": 1}).to_list(1000)
        plot_ids = [str(p["_id"]) for p in user_plots]
        query["plotId"] = {"$in": plot_ids}

    if status:
        query["status"] = status

    crops = await db.crops.find(query).sort("createdAt", -1).to_list(500)
    return [_serialize(c) for c in crops]


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: str, user=Depends(get_current_user)):
    db = get_database()
    crop = await db.crops.find_one({"_id": _oid(crop_id)})
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    await _verify_plot_owner(crop["plotId"], user["_id"], db)
    return _serialize(crop)


@router.put("/{crop_id}", response_model=CropResponse)
async def update_crop(crop_id: str, data: CropUpdate, user=Depends(get_current_user)):
    db = get_database()
    crop = await db.crops.find_one({"_id": _oid(crop_id)})
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    await _verify_plot_owner(crop["plotId"], user["_id"], db)

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await db.crops.find_one_and_update(
        {"_id": _oid(crop_id)}, {"$set": updates}, return_document=True
    )
    return _serialize(updated)


@router.delete("/{crop_id}", status_code=204)
async def delete_crop(crop_id: str, user=Depends(get_current_user)):
    db = get_database()
    crop = await db.crops.find_one({"_id": _oid(crop_id)})
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    await _verify_plot_owner(crop["plotId"], user["_id"], db)
    await db.crops.delete_one({"_id": _oid(crop_id)})
