# ─── AgriFlow AI — Expense & Inventory Routes ─────────────────────────────────
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional

from ..database import get_database
from ..schemas.finance import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    InventoryCreate, InventoryUpdate, InventoryResponse,
)
from ..dependencies import get_current_user

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _oid(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


async def _user_farm_ids(user_id, db) -> list[str]:
    farms = await db.farms.find({"ownerId": user_id}, {"_id": 1}).to_list(500)
    return [str(f["_id"]) for f in farms]


def _stock_status(quantity: float, minimum: float) -> str:
    if quantity <= 0:
        return "Out of Stock"
    elif quantity <= minimum:
        return "Low Stock"
    return "Normal"


# ─── Expenses ─────────────────────────────────────────────────────────────────
expense_router = APIRouter()


def _ser_expense(doc: dict) -> ExpenseResponse:
    return ExpenseResponse(
        id=str(doc["_id"]),
        farmId=str(doc["farmId"]),
        plotId=str(doc["plotId"]) if doc.get("plotId") else None,
        category=doc["category"],
        amount=doc["amount"],
        date=doc["date"],
        description=doc.get("description"),
        createdAt=doc["createdAt"],
    )


@expense_router.post("", response_model=ExpenseResponse, status_code=201)
async def create_expense(data: ExpenseCreate, user=Depends(get_current_user)):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    if data.farmId not in farm_ids:
        raise HTTPException(status_code=403, detail="Farm access denied")

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.expenses.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _ser_expense(doc)


@expense_router.get("", response_model=list[ExpenseResponse])
async def list_expenses(
    farmId: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    query: dict = {"farmId": {"$in": farm_ids}}
    if farmId:
        if farmId not in farm_ids:
            raise HTTPException(status_code=403, detail="Farm access denied")
        query["farmId"] = farmId
    if category:
        query["category"] = category

    docs = await db.expenses.find(query).sort("date", -1).to_list(1000)
    return [_ser_expense(d) for d in docs]


@expense_router.get("/summary")
async def expense_summary(
    farmId: Optional[str] = Query(default=None),
    user=Depends(get_current_user),
):
    """Return total expenses grouped by category + monthly totals."""
    from collections import defaultdict
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    query: dict = {"farmId": {"$in": farm_ids}}
    if farmId:
        if farmId not in farm_ids:
            raise HTTPException(status_code=403, detail="Farm access denied")
        query["farmId"] = farmId

    docs = await db.expenses.find(query).to_list(5000)

    by_category: dict = defaultdict(float)
    by_month: dict = defaultdict(float)

    for d in docs:
        by_category[d["category"]] += d["amount"]
        month_key = d["date"].strftime("%Y-%m") if hasattr(d["date"], "strftime") else "unknown"
        by_month[month_key] += d["amount"]

    return {
        "total": sum(by_category.values()),
        "byCategory": dict(by_category),
        "byMonth": dict(sorted(by_month.items())),
    }


@expense_router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: str, data: ExpenseUpdate, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.expenses.find_one({"_id": _oid(expense_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Expense not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await db.expenses.find_one_and_update(
        {"_id": _oid(expense_id)}, {"$set": updates}, return_document=True
    )
    return _ser_expense(updated)


@expense_router.delete("/{expense_id}", status_code=204)
async def delete_expense(expense_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.expenses.find_one({"_id": _oid(expense_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Expense not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.expenses.delete_one({"_id": _oid(expense_id)})


# ─── Inventory ────────────────────────────────────────────────────────────────
inventory_router = APIRouter()


def _ser_inventory(doc: dict) -> InventoryResponse:
    qty = doc.get("quantity", 0)
    mini = doc.get("minimumLevel", 0)
    return InventoryResponse(
        id=str(doc["_id"]),
        farmId=str(doc["farmId"]),
        name=doc["name"],
        category=doc["category"],
        quantity=qty,
        unit=doc.get("unit", "kg"),
        minimumLevel=mini,
        cost=doc.get("cost", 0.0),
        stockStatus=_stock_status(qty, mini),
        createdAt=doc["createdAt"],
    )


@inventory_router.post("", response_model=InventoryResponse, status_code=201)
async def create_inventory(data: InventoryCreate, user=Depends(get_current_user)):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    if data.farmId not in farm_ids:
        raise HTTPException(status_code=403, detail="Farm access denied")

    doc = {**data.model_dump(), "createdAt": datetime.now(timezone.utc)}
    result = await db.inventory.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _ser_inventory(doc)


@inventory_router.get("", response_model=list[InventoryResponse])
async def list_inventory(
    farmId: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    lowStock: Optional[bool] = Query(default=None),
    user=Depends(get_current_user),
):
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    query: dict = {"farmId": {"$in": farm_ids}}
    if farmId:
        if farmId not in farm_ids:
            raise HTTPException(status_code=403, detail="Farm access denied")
        query["farmId"] = farmId
    if category:
        query["category"] = category

    docs = await db.inventory.find(query).sort("name", 1).to_list(500)
    result = [_ser_inventory(d) for d in docs]

    if lowStock is True:
        result = [r for r in result if r.stockStatus in ("Low Stock", "Out of Stock")]

    return result


@inventory_router.get("/alerts")
async def inventory_alerts(user=Depends(get_current_user)):
    """Return all low-stock and out-of-stock items."""
    db = get_database()
    farm_ids = await _user_farm_ids(user["_id"], db)
    docs = await db.inventory.find({"farmId": {"$in": farm_ids}}).to_list(1000)
    alerts = []
    for d in docs:
        status = _stock_status(d.get("quantity", 0), d.get("minimumLevel", 0))
        if status != "Normal":
            alerts.append({
                "id": str(d["_id"]),
                "name": d["name"],
                "category": d["category"],
                "quantity": d.get("quantity", 0),
                "unit": d.get("unit", "kg"),
                "minimumLevel": d.get("minimumLevel", 0),
                "stockStatus": status,
                "farmId": d["farmId"],
            })
    return alerts


@inventory_router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory(item_id: str, data: InventoryUpdate, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.inventory.find_one({"_id": _oid(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await db.inventory.find_one_and_update(
        {"_id": _oid(item_id)}, {"$set": updates}, return_document=True
    )
    return _ser_inventory(updated)


@inventory_router.delete("/{item_id}", status_code=204)
async def delete_inventory(item_id: str, user=Depends(get_current_user)):
    db = get_database()
    doc = await db.inventory.find_one({"_id": _oid(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    farm_ids = await _user_farm_ids(user["_id"], db)
    if doc["farmId"] not in farm_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    await db.inventory.delete_one({"_id": _oid(item_id)})
