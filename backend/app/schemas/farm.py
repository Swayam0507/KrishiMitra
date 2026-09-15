# ─── AgriFlow AI — Farm Schemas ───────────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

SOIL_TYPES = ["Clay", "Sandy", "Loamy", "Silty", "Peaty", "Chalky", "Black Cotton", "Red Laterite"]
IRRIGATION_TYPES = ["Drip", "Sprinkler", "Flood", "Furrow", "Rain-fed", "Canal", "Borewell", "Other"]
AREA_UNITS = ["acres", "hectares", "bigha", "sq_meters"]


class FarmCreate(BaseModel):
    farmName: str = Field(..., min_length=2, max_length=200)
    location: str = Field(..., min_length=2, max_length=300)
    area: float = Field(..., gt=0)
    areaUnit: str = Field(default="acres")
    soilType: str = Field(default="Loamy")
    irrigationType: str = Field(default="Drip")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class FarmUpdate(BaseModel):
    farmName: Optional[str] = Field(default=None, min_length=2, max_length=200)
    location: Optional[str] = None
    area: Optional[float] = Field(default=None, gt=0)
    areaUnit: Optional[str] = None
    soilType: Optional[str] = None
    irrigationType: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class FarmResponse(BaseModel):
    id: str
    farmName: str
    location: str
    area: float
    areaUnit: str
    soilType: str
    irrigationType: str
    latitude: Optional[float]
    longitude: Optional[float]
    ownerId: str
    createdAt: datetime
