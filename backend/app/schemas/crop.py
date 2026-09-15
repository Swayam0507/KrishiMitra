# ─── AgriFlow AI — Crop Schemas ───────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

VALID_STAGES = ["Seed", "Germination", "Vegetative", "Flowering", "Fruiting", "Harvest"]
VALID_STATUS = ["Active", "Completed", "Failed"]


class CropCreate(BaseModel):
    plotId: str
    cropName: str = Field(..., min_length=2, max_length=200)
    variety: Optional[str] = None
    plantingDate: datetime
    expectedHarvestDate: Optional[datetime] = None
    currentStage: str = Field(default="Seed")
    seedSource: Optional[str] = None
    area: float = Field(..., gt=0)
    status: str = Field(default="Active")


class CropUpdate(BaseModel):
    cropName: Optional[str] = None
    variety: Optional[str] = None
    plantingDate: Optional[datetime] = None
    expectedHarvestDate: Optional[datetime] = None
    currentStage: Optional[str] = None
    seedSource: Optional[str] = None
    area: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None


class CropResponse(BaseModel):
    id: str
    plotId: str
    cropName: str
    variety: Optional[str]
    plantingDate: datetime
    expectedHarvestDate: Optional[datetime]
    currentStage: str
    seedSource: Optional[str]
    area: float
    status: str
    createdAt: datetime
