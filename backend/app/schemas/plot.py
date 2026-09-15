# ─── AgriFlow AI — Plot Schemas ───────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

CROP_STAGES = ["Seed", "Germination", "Vegetative", "Flowering", "Fruiting", "Harvest"]
WATER_AVAILABILITY = ["Adequate", "Moderate", "Low", "Very Low", "None"]


class PlotCreate(BaseModel):
    farmId: str
    plotName: str = Field(..., min_length=1, max_length=200)
    area: float = Field(..., gt=0)
    soilType: Optional[str] = "Loamy"
    soilPH: Optional[float] = Field(default=7.0, ge=0.0, le=14.0)
    soilMoisture: Optional[float] = Field(default=50.0, ge=0.0, le=100.0)
    waterAvailability: Optional[str] = "Adequate"
    currentCrop: Optional[str] = None
    cropStage: Optional[str] = None


class PlotUpdate(BaseModel):
    plotName: Optional[str] = None
    area: Optional[float] = Field(default=None, gt=0)
    soilType: Optional[str] = None
    soilPH: Optional[float] = Field(default=None, ge=0.0, le=14.0)
    soilMoisture: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    waterAvailability: Optional[str] = None
    currentCrop: Optional[str] = None
    cropStage: Optional[str] = None


class PlotResponse(BaseModel):
    id: str
    farmId: str
    plotName: str
    area: float
    soilType: Optional[str]
    soilPH: Optional[float]
    soilMoisture: Optional[float]
    waterAvailability: Optional[str]
    currentCrop: Optional[str]
    cropStage: Optional[str]
    createdAt: datetime
