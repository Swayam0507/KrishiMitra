# ─── AgriFlow AI — Activity & Worker Routes ───────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..schemas.activity import (
    ActivityCreate, ActivityUpdate, ActivityResponse,
    WorkerCreate, WorkerUpdate, WorkerResponse,
)
from ..dependencies import get_current_user

# ─── Activities ───────────────────────────────────────────────────────────────
activity_router = APIRouter()


def _serialize_activity(doc: dict) -> ActivityResponse:
    return ActivityResponse(
        id=str(doc["_id"]),
        farmId=str(doc["farmId"]),
        plotId=str(doc["plotId"]) if doc.get("plotId") else None,
        activityType=doc["activityType"],
        date=doc["date"],
        workerId=str(doc["workerId"]) if doc.get("workerId") else None,
        cost=doc.get("cost", 0.0),
        notes=doc.get("notes"),
        status=doc.get("status", "Pending"),
        createdAt=doc["createdAt"],
    )


def _oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


async def _user_farm_ids(user_id, db) -> list[str]:
    farms = await db.farms.find({"ownerId": user_id}, {"_id": 1}).to_list(500)
    return [str(f["_id"]) for f in farms]


@activity_router.post("", response_model=ActivityResponse, status_code=201)
async def create_activity(data: ActivityCreate, user=Depends(get_current_user)):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    if data.farmId not in farm_ids:
        raise HTTPException(status_code=403, detail="Farm access denied")

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.activities.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_activity(doc)


@activity_router.get("", response_model=list[ActivityResponse])
async def list_activities(
    farmId: Optional[str] = Query(default=None),
    plotId: Optional[str] = Query(default=None),
    activityType: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    query: dict = {"farmId": {"$in": farm_ids}}

    if farmId:
        if farmId not in farm_ids:
            raise HTTPException(status_code=403, detail="Farm access denied")
        query["farmId"] = farmId
    if plotId:
        query["plotId"] = plotId
    if activityType:
        query["activityType"] = activityType
    if status:
        query["status"] = status

    docs = await db.activities.find(query).sort("date", -1).to_list(500)
    return [_serialize_activity(d) for d in docs]


@activity_router.get("/today", response_model=list[ActivityResponse])
async def today_activities(user=Depends(get_current_user)):
    """Activities scheduled for today."""
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    today = datetime.now(timezone.utc).date()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    end = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)

    docs = await db.activities.find({
        "farmId": {"$in": farm_ids},
        "date": {"$gte": start, "$lte": end},
    }).sort("date", 1).to_list(100)
    return [_serialize_activity(d) for d in docs]


@activity_router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(activity_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.activities.find_one({"_id": _oid(activity_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    return _serialize_activity(doc)


@activity_router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(activity_id: str, data: ActivityUpdate, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.activities.find_one({"_id": _oid(activity_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await db.activities.find_one_and_update(
        {"_id": _oid(activity_id)}, {"$set": updates}, return_document=True
    )
    return _serialize_activity(updated)


@activity_router.delete("/{activity_id}", status_code=204)
async def delete_activity(activity_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.activities.find_one({"_id": _oid(activity_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.activities.delete_one({"_id": _oid(activity_id)})


# ─── Workers ──────────────────────────────────────────────────────────────────
worker_router = APIRouter()


def _serialize_worker(doc: dict) -> WorkerResponse:
    return WorkerResponse(
        id=str(doc["_id"]),
        farmId=str(doc["farmId"]),
        name=doc["name"],
        phone=doc.get("phone"),
        role=doc.get("role", "Field Worker"),
        dailyWage=doc.get("dailyWage", 0.0),
        availability=doc.get("availability", "Available"),
        skills=doc.get("skills", []),
        createdAt=doc["createdAt"],
    )


@worker_router.post("", response_model=WorkerResponse, status_code=201)
async def create_worker(data: WorkerCreate, user=Depends(get_current_user)):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    if data.farmId not in farm_ids:
        raise HTTPException(status_code=403, detail="Farm access denied")

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.workers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize_worker(doc)


@worker_router.get("", response_model=list[WorkerResponse])
async def list_workers(
    farmId: Optional[str] = Query(default=None),
    availability: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    query: dict = {"farmId": {"$in": farm_ids}}

    if farmId:
        if farmId not in farm_ids:
            raise HTTPException(status_code=403, detail="Farm access denied")
        query["farmId"] = farmId
    if availability:
        query["availability"] = availability

    docs = await db.workers.find(query).sort("name", 1).to_list(500)
    return [_serialize_worker(d) for d in docs]


@worker_router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(worker_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.workers.find_one({"_id": _oid(worker_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Worker not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    return _serialize_worker(doc)


@worker_router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(worker_id: str, data: WorkerUpdate, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.workers.find_one({"_id": _oid(worker_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Worker not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await db.workers.find_one_and_update(
        {"_id": _oid(worker_id)}, {"$set": updates}, return_document=True
    )
    return _serialize_worker(updated)


@worker_router.delete("/{worker_id}", status_code=204)
async def delete_worker(worker_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.workers.find_one({"_id": _oid(worker_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Worker not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.workers.delete_one({"_id": _oid(worker_id)})


@worker_router.get("/{worker_id}/history")
async def worker_activity_history(worker_id: str, user=Depends(get_current_user)):
    """Return all activities assigned to this worker."""
    db = get_database()
    doc = await db.workers.find_one({"_id": _oid(worker_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Worker not found")

    activities = await db.activities.find({"workerId": worker_id}).sort("date", -1).to_list(200)
    return {
        "worker": _serialize_worker(doc),
        "activities": [
            {
                "id": str(a["_id"]),
                "activityType": a["activityType"],
                "date": a["date"],
                "status": a.get("status"),
                "cost": a.get("cost", 0),
            }
            for a in activities
        ],
    }
