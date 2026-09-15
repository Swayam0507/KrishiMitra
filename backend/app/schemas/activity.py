# ─── AgriFlow AI — Activity Schemas ───────────────────────────────────────────
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

ACTIVITY_TYPES = [
    "Planting", "Irrigation", "Fertilization", "Pesticide",
    "Weeding", "Harvesting", "Disease Inspection", "Soil Testing", "Other",
]
ACTIVITY_STATUS = ["Pending", "In Progress", "Completed", "Cancelled"]


class ActivityCreate(BaseModel):
    farmId: str
    plotId: Optional[str] = None
    activityType: str = Field(..., description=f"One of: {ACTIVITY_TYPES}")
    date: datetime
    workerId: Optional[str] = None
    cost: float = Field(default=0.0, ge=0)
    notes: Optional[str] = None
    status: str = Field(default="Pending")


class ActivityUpdate(BaseModel):
    activityType: Optional[str] = None
    date: Optional[datetime] = None
    workerId: Optional[str] = None
    cost: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = None
    status: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    farmId: str
    plotId: Optional[str]
    activityType: str
    date: datetime
    workerId: Optional[str]
    cost: float
    notes: Optional[str]
    status: str
    createdAt: datetime


# ─── Worker Schemas ────────────────────────────────────────────────────────────
WORKER_ROLES = ["Field Worker", "Supervisor", "Driver", "Technician", "Agronomist", "Other"]
AVAILABILITY_STATUS = ["Available", "Assigned", "On Leave", "Unavailable"]


class WorkerCreate(BaseModel):
    farmId: str
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    role: str = Field(default="Field Worker")
    dailyWage: float = Field(default=0.0, ge=0)
    availability: str = Field(default="Available")
    skills: list[str] = []


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    dailyWage: Optional[float] = Field(default=None, ge=0)
    availability: Optional[str] = None
    skills: Optional[list[str]] = None
    farmId: Optional[str] = None


class WorkerResponse(BaseModel):
    id: str
    farmId: str
    name: str
    phone: Optional[str]
    role: str
    dailyWage: float
    availability: str
    skills: list[str]
    createdAt: datetime
