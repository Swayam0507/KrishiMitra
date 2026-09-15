# ─── AgriFlow AI — FastAPI Application Entry Point ────────────────────────────
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import get_settings
from .database import connect_db, disconnect_db

# ── Route imports ──────────────────────────────────────────────────────────────
from .routes.health import router as health_router
from .routes.auth import router as auth_router
from .routes.farms import router as farms_router
from .routes.plots import router as plots_router
from .routes.crops import router as crops_router
from .routes.activities import activity_router, worker_router
from .routes.finance import expense_router, inventory_router
from .routes.disease import router as disease_router
from .routes.risk import router as risk_router
from .routes.ai_routes import (
    recommendation_router,
    irrigation_router,
    weather_router,
)
from .routes.health_score import router as health_score_router
from .routes.sustainability import router as sustainability_router
from .routes.sensors import router as sensors_router
from .routes.anomaly import router as anomaly_router
from .routes.intelligence import router as intelligence_router
from .routes.advisor import router as advisor_router
from .routes.assistant import router as assistant_router
from .routes.alerts import router as alerts_router


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


# ── App factory ───────────────────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent Farm Management, Crop Health & AI Agricultural Advisor",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploads ───────────────────────────────────────────
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router,          prefix="/api")
app.include_router(auth_router,            prefix="/api/auth",           tags=["Authentication"])
app.include_router(farms_router,           prefix="/api/farms",          tags=["Farms"])
app.include_router(plots_router,           prefix="/api/plots",          tags=["Plots"])
app.include_router(crops_router,           prefix="/api/crops",          tags=["Crops"])
app.include_router(activity_router,        prefix="/api/activities",     tags=["Activities"])
app.include_router(worker_router,          prefix="/api/workers",        tags=["Workers"])
app.include_router(expense_router,         prefix="/api/expenses",       tags=["Expenses"])
app.include_router(inventory_router,       prefix="/api/inventory",      tags=["Inventory"])
app.include_router(disease_router,         prefix="/api/disease",        tags=["Disease Detection"])
app.include_router(risk_router,            prefix="/api/risk",           tags=["Disease Risk"])
app.include_router(recommendation_router,  prefix="/api/recommendation", tags=["Crop Recommendation"])
app.include_router(irrigation_router,      prefix="/api/irrigation",     tags=["Smart Irrigation"])
app.include_router(weather_router,         prefix="/api/weather",        tags=["Weather"])
app.include_router(health_score_router,    prefix="/api/farm-health",    tags=["Farm Health Score"])
app.include_router(sustainability_router,  prefix="/api/sustainability", tags=["Sustainability"])
app.include_router(sensors_router,         prefix="/api/sensors",        tags=["IoT Sensors"])
app.include_router(anomaly_router,         prefix="/api/anomaly",        tags=["Anomaly Detection"])
app.include_router(intelligence_router,    prefix="/api/intelligence",   tags=["Intelligence Engine"])
app.include_router(advisor_router,         prefix="/api/advisor",        tags=["Agentic Advisor"])
app.include_router(assistant_router,       prefix="/api/assistant",      tags=["GenAI Assistant"])
app.include_router(alerts_router,          prefix="/api/alerts",         tags=["Alerts"])


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs",
        "health": "/api/health",
    }
