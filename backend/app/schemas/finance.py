# ─── AgriFlow AI — Expense & Inventory Schemas ────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ─── Expense ──────────────────────────────────────────────────────────────────
EXPENSE_CATEGORIES = [
    "Seeds", "Fertilizer", "Pesticides", "Labor",
    "Water", "Electricity", "Equipment", "Transport", "Other",
]


class ExpenseCreate(BaseModel):
    farmId: str
    plotId: Optional[str] = None
    category: str = Field(..., description=f"One of: {EXPENSE_CATEGORIES}")
    amount: float = Field(..., ge=0)
    date: datetime
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = Field(default=None, ge=0)
    date: Optional[datetime] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    farmId: str
    plotId: Optional[str]
    category: str
    amount: float
    date: datetime
    description: Optional[str]
    createdAt: datetime


# ─── Inventory ────────────────────────────────────────────────────────────────
INVENTORY_CATEGORIES = ["Seeds", "Fertilizers", "Pesticides", "Equipment", "Other"]


class InventoryCreate(BaseModel):
    farmId: str
    name: str = Field(..., min_length=2, max_length=200)
    category: str = Field(..., description=f"One of: {INVENTORY_CATEGORIES}")
    quantity: float = Field(..., ge=0)
    unit: str = Field(default="kg")
    minimumLevel: float = Field(default=0.0, ge=0)
    cost: float = Field(default=0.0, ge=0)


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = Field(default=None, ge=0)
    unit: Optional[str] = None
    minimumLevel: Optional[float] = Field(default=None, ge=0)
    cost: Optional[float] = Field(default=None, ge=0)


class InventoryResponse(BaseModel):
    id: str
    farmId: str
    name: str
    category: str
    quantity: float
    unit: str
    minimumLevel: float
    cost: float
    stockStatus: str          # "Normal" | "Low Stock" | "Out of Stock"
    createdAt: datetime


# ─── Disease ──────────────────────────────────────────────────────────────────
class DiseaseHistoryResponse(BaseModel):
    id: str
    userId: str
    imagePath: str
    cropType: Optional[str]
    growthStage: Optional[str]
    disease: str
    confidence: float
    risk: str
    recommendations: list[str]
    modelStatus: str          # "PREDICTED" | "MODEL NOT TRAINED"
    gradcamPath: Optional[str]
    createdAt: datetime
