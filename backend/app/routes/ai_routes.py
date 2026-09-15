# ─── AgriFlow AI — Crop Recommendation & Irrigation & Weather Routes ──────────
"""
Crop Recommendation:   POST /api/recommendation/crop
Smart Irrigation:      POST /api/irrigation/advise
Weather:               GET  /api/weather/current
                       GET  /api/weather/forecast
"""
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import httpx

from ..database import get_database
from ..dependencies import get_current_user
from ..config import get_settings

# ─── Crop Recommendation ──────────────────────────────────────────────────────
recommendation_router = APIRouter()

ML_PATH = Path(__file__).resolve().parents[3] / "ml"


def _import_crop_predictor():
    sys.path.insert(0, str(ML_PATH))
    try:
        from crop_recommendation.predict import CropPredictor
        return CropPredictor()
    except Exception:
        return None


class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(..., ge=0, description="N value (kg/ha)")
    phosphorus: float = Field(..., ge=0, description="P value (kg/ha)")
    potassium: float = Field(..., ge=0, description="K value (kg/ha)")
    temperature: float = Field(..., description="°C")
    humidity: float = Field(..., ge=0, le=100, description="%")
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, description="mm")
    soilType: Optional[str] = None
    season: Optional[str] = None
    location: Optional[str] = None
    previousCrop: Optional[str] = None
    waterAvailability: Optional[str] = None


@recommendation_router.post("/crop")
async def recommend_crop(data: CropRecommendationRequest, user=Depends(get_current_user)):
    predictor = _import_crop_predictor()

    if predictor is None:
        return {
            "modelStatus": "MODEL NOT TRAINED",
            "recommendation": None,
            "score": None,
            "alternatives": [],
            "reason": "Train the model first: cd ml && python crop_recommendation/train.py",
        }

    try:
        result = predictor.predict(data.model_dump())
        db = get_database()
        await db.crop_recommendations.insert_one({
            "userId": str(user["_id"]),
            "inputs": data.model_dump(),
            "result": result,
        })
        return {**result, "modelStatus": "PREDICTED"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}")


# ─── Smart Irrigation ─────────────────────────────────────────────────────────
irrigation_router = APIRouter()


def _import_irrigation():
    sys.path.insert(0, str(ML_PATH))
    try:
        from irrigation.predict import IrrigationAdvisor
        return IrrigationAdvisor()
    except Exception:
        return None


class IrrigationRequest(BaseModel):
    soilMoisture: float = Field(..., ge=0, le=100, description="% volumetric")
    temperature: float = Field(..., description="°C")
    humidity: float = Field(..., ge=0, le=100, description="%")
    rainProbability: float = Field(default=0.0, ge=0, le=100, description="%")
    cropType: Optional[str] = None
    growthStage: Optional[str] = None
    soilType: Optional[str] = None
    recentRainfall: float = Field(default=0.0, ge=0, description="mm in last 24h")


@irrigation_router.post("/advise")
async def irrigation_advice(data: IrrigationRequest, user=Depends(get_current_user)):
    advisor = _import_irrigation()

    if advisor is None:
        # Rule-based fallback
        from ..services.irrigation_rules import rule_based_advice
        result = rule_based_advice(data.model_dump())
        result["modelStatus"] = "RULE-BASED (ML not trained)"
        return result

    try:
        result = advisor.advise(data.model_dump())
        return {**result, "modelStatus": "ML+RULES"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Irrigation advisor error: {exc}")


# ─── Weather ──────────────────────────────────────────────────────────────────
weather_router = APIRouter()


@weather_router.get("/current")
async def current_weather(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    city: Optional[str] = None,
    user=Depends(get_current_user),
):
    settings = get_settings()

    if not settings.openweather_api_key:
        return _demo_weather()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if lat is not None and lon is not None:
                params = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "metric"}
            elif city:
                params = {"q": city, "appid": settings.openweather_api_key, "units": "metric"}
            else:
                return _demo_weather()

            resp = await client.get("https://api.openweathermap.org/data/2.5/weather", params=params)
            resp.raise_for_status()
            data = resp.json()

            return {
                "source": "OpenWeatherMap",
                "city": data.get("name"),
                "temperature": data["main"]["temp"],
                "feelsLike": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "windSpeed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "rainProbability": None,
                "recommendations": _weather_recommendations(data),
            }
    except Exception as exc:
        return {**_demo_weather(), "warning": f"Weather API error: {exc}. Showing demo data."}


@weather_router.get("/forecast")
async def weather_forecast(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    city: Optional[str] = None,
    user=Depends(get_current_user),
):
    settings = get_settings()

    if not settings.openweather_api_key:
        return _demo_forecast()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if lat is not None and lon is not None:
                params = {"lat": lat, "lon": lon, "appid": settings.openweather_api_key, "units": "metric"}
            elif city:
                params = {"q": city, "appid": settings.openweather_api_key, "units": "metric"}
            else:
                return _demo_forecast()

            resp = await client.get("https://api.openweathermap.org/data/2.5/forecast", params=params)
            resp.raise_for_status()
            data = resp.json()

            daily = {}
            for item in data["list"]:
                day = item["dt_txt"][:10]
                if day not in daily:
                    daily[day] = {
                        "date": day,
                        "tempMin": item["main"]["temp_min"],
                        "tempMax": item["main"]["temp_max"],
                        "humidity": item["main"]["humidity"],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["icon"],
                        "rainMm": item.get("rain", {}).get("3h", 0),
                    }
                else:
                    daily[day]["tempMin"] = min(daily[day]["tempMin"], item["main"]["temp_min"])
                    daily[day]["tempMax"] = max(daily[day]["tempMax"], item["main"]["temp_max"])

            return {
                "source": "OpenWeatherMap",
                "city": data.get("city", {}).get("name"),
                "forecast": list(daily.values())[:7],
            }
    except Exception as exc:
        return {**_demo_forecast(), "warning": f"Weather API error: {exc}"}


# ─── Demo / Fallback Weather ──────────────────────────────────────────────────
def _demo_weather():
    return {
        "source": "SIMULATED DATA",
        "city": "Demo Location",
        "temperature": 28.5,
        "feelsLike": 31.2,
        "humidity": 65,
        "windSpeed": 3.2,
        "description": "Partly cloudy",
        "icon": "02d",
        "rainProbability": 20,
        "recommendations": [
            "Good conditions for field work today.",
            "Monitor soil moisture — moderate humidity.",
        ],
    }


def _demo_forecast():
    import datetime
    today = datetime.date.today()
    forecast = []
    temps = [(24, 32), (22, 30), (25, 33), (26, 34), (23, 31), (21, 29), (24, 32)]
    for i, (mn, mx) in enumerate(temps):
        day = today + datetime.timedelta(days=i)
        forecast.append({
            "date": str(day),
            "tempMin": mn,
            "tempMax": mx,
            "humidity": 60 + (i % 3) * 5,
            "description": ["Sunny", "Partly cloudy", "Cloudy", "Light rain", "Sunny", "Sunny", "Cloudy"][i],
            "rainMm": [0, 0, 0, 8, 0, 0, 2][i],
        })
    return {
        "source": "SIMULATED DATA",
        "city": "Demo Location",
        "forecast": forecast,
    }


def _weather_recommendations(data: dict) -> list[str]:
    recommendations = []
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    rain = data.get("rain", {}).get("1h", 0)

    if rain > 5:
        recommendations.append("🌧 Delay irrigation — rainfall expected.")
    if humidity > 80:
        recommendations.append("⚠ Monitor for fungal disease — humidity is high.")
    if wind > 10:
        recommendations.append("💨 Avoid pesticide spraying — strong wind expected.")
    if temp > 35:
        recommendations.append("🌡 High temperature — consider extra irrigation for sensitive crops.")
    if temp < 10:
        recommendations.append("❄ Low temperature — protect sensitive seedlings.")
    if not recommendations:
        recommendations.append("✅ Weather conditions look favourable for farming activities.")

    return recommendations
