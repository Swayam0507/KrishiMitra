# ─── AgriFlow AI — GenAI Farmer Assistant (Phase 28 + 29) ────────────────────
"""
Grounded farmer assistant using Gemini API.

Provider abstraction:
  GeminiProvider  — uses GEMINI_API_KEY from environment
  DemoProvider    — rule-based fallback when API key is not set

The assistant accesses real farm context before answering:
  Farm, Plot, Crop, Disease Result, Weather (if available),
  Sensor Data, Irrigation Recommendation, Sustainability, Alerts.

Never invents farm data. Clearly labels Demo mode.

Agricultural Knowledge Base (Phase 29) is embedded as a structured guide
given to Gemini as part of the system prompt.
"""
import httpx
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..database import get_database
from ..dependencies import get_current_user
from ..config import get_settings
from ..services.irrigation_rules import rule_based_advice

router = APIRouter()

# ─── Agricultural Knowledge Base (Phase 29) ────────────────────────────────────
AG_KNOWLEDGE = """
## Agricultural Knowledge Base

### Crop Diseases
- Fungal diseases (late blight, early blight, powdery mildew) thrive in high humidity (>80%) and moderate temperatures (20–30°C).
- Bacterial diseases spread through water splashing and wounds.
- Viral diseases are often spread by insect vectors (aphids, whiteflies).
- Key preventive measure: crop rotation, proper spacing, IPM (Integrated Pest Management).

### Irrigation Guidelines
- Optimal soil moisture for most crops: 40–70% (volumetric).
- Drip irrigation efficiency: ~90–95%.
- Sprinkler efficiency: ~75–85%.
- Flood irrigation efficiency: ~40–60%.
- Irrigate early morning to reduce evaporation and leaf wetness.

### Soil Health
- Optimal soil pH: 6.0–7.5 for most crops.
- Acidic soil (pH < 6): apply agricultural lime.
- Alkaline soil (pH > 7.5): apply sulphur or gypsum.
- Good soil moisture range: 40–70%.
- Regular soil testing (every 6 months) is recommended.

### Crop Care
- Planting dates must match local climate and season.
- Spacing prevents competition and reduces disease spread.
- Fertiliser application should be based on soil test results.
- Organic matter improves soil structure and water retention.

### Sustainability
- Water efficiency: drip > sprinkler > flood.
- Crop rotation reduces disease pressure and improves soil.
- Cover cropping between seasons prevents erosion.
- Composting and organic fertilisers reduce external input costs.

### General Practices
- Monitor crops at least twice per week.
- Keep activity records for traceability.
- Store agrochemicals safely and follow label instructions.
- Train farm workers on basic IPM and safe chemical handling.

### IMPORTANT DISCLAIMERS
- AI-generated guidance is GENERAL ADVICE, not a certified agronomic prescription.
- For specific disease treatment: consult a qualified agronomist.
- Model predictions carry uncertainty — always verify in the field.
- ESTIMATED savings and scores are indicative, not measurements.
"""


# ─── Farm context loader ───────────────────────────────────────────────────────

async def _build_farm_context(user_id: str, db) -> str:
    """Collect real farm data to ground assistant responses."""
    ctx_lines = ["## Current Farm Context (from AgriFlow AI database)\n"]

    # Farms
    farms = await db.farms.find({"ownerId": user_id}).to_list(5)
    if farms:
        ctx_lines.append(f"**Farms ({len(farms)}):**")
        for f in farms:
            ctx_lines.append(
                f"  - {f['farmName']}: {f['area']} {f.get('areaUnit','acres')}, "
                f"location={f['location']}, soil={f['soilType']}, irrigation={f['irrigationType']}"
            )

    # Active crops
    user_farm_ids = [str(f["_id"]) for f in farms]
    user_plot_ids = []
    if user_farm_ids:
        plots = await db.plots.find({"farmId": {"$in": user_farm_ids}}).to_list(50)
        user_plot_ids = [str(p["_id"]) for p in plots]
        active_crops = await db.crops.find({
            "plotId": {"$in": user_plot_ids}, "status": "Active"
        }).to_list(10)
        if active_crops:
            ctx_lines.append(f"\n**Active Crops ({len(active_crops)}):**")
            for c in active_crops:
                ctx_lines.append(
                    f"  - {c['cropName']} ({c.get('variety', '')}): Stage={c.get('currentStage')}, "
                    f"Area={c['area']} acres"
                )

    # Latest sensor reading
    if user_farm_ids:
        sensor = await db.sensor_readings.find_one(
            {"farmId": {"$in": user_farm_ids}}, sort=[("timestamp", -1)]
        )
        if sensor:
            ctx_lines.append(
                f"\n**Latest Sensor Reading (SIMULATED):**\n"
                f"  Soil Moisture: {sensor.get('soilMoisture')}%  |  "
                f"Temperature: {sensor.get('temperature')}°C  |  "
                f"Humidity: {sensor.get('humidity')}%  |  "
                f"Soil pH: {sensor.get('soilPH')}\n"
                f"  (Reading from: {sensor.get('timestamp')})"
            )

    # Latest disease prediction
    pred = await db.disease_predictions.find_one(
        {"userId": str(user_id)}, sort=[("createdAt", -1)]
    )
    if pred and pred.get("disease"):
        ctx_lines.append(
            f"\n**Latest Disease Detection:**\n"
            f"  Disease: {pred['disease']}  |  "
            f"Confidence: {pred.get('confidence', 0)*100:.0f}%  |  "
            f"Risk: {pred.get('risk')}  |  "
            f"Status: {pred.get('modelStatus')}"
        )

    # Latest irrigation advice
    irr = await db.activities.find_one(
        {"farmId": {"$in": user_farm_ids}, "activityType": "Irrigation"},
        sort=[("date", -1)],
    )

    # Inventory alerts
    low_stock = []
    items = await db.inventory.find({"farmId": {"$in": user_farm_ids}}).to_list(100)
    for item in items:
        if item.get("quantity", 0) <= item.get("minimumLevel", 0):
            low_stock.append(f"{item['name']} ({item.get('quantity')} {item.get('unit','')})")
    if low_stock:
        ctx_lines.append(f"\n**Low/Out-of-Stock Inventory:** {', '.join(low_stock[:5])}")

    # Risk summary
    risk = await db.disease_risk.find_one(
        {"userId": str(user_id)}, sort=[("createdAt", -1)]
    )
    if risk:
        ctx_lines.append(
            f"\n**Latest Disease Risk:** Score={risk.get('riskScore')}/100, "
            f"Band={risk.get('riskBand')}"
        )

    if len(ctx_lines) <= 1:
        ctx_lines.append("No farm data available yet. Please add farms and crops first.")

    return "\n".join(ctx_lines)


# ─── Provider abstraction ──────────────────────────────────────────────────────

async def _gemini_response(message: str, context: str, history: list[dict]) -> str:
    """Call Gemini API with grounded context."""
    settings = get_settings()

    system_prompt = f"""You are AgriFlow AI — an intelligent agricultural advisor for Indian farmers.
You have access to the farmer's actual farm data shown below.

RULES:
1. Always use the provided farm data to answer questions. Never invent farm data.
2. Clearly distinguish: AI Prediction | General Guidance | Estimated Information.
3. For disease/health decisions: recommend consulting a qualified agronomist.
4. Keep language simple and farmer-friendly.
5. If asked about data you don't have, say so clearly.
6. Support queries in English, Hindi, and Gujarati — respond in the same language as the user.

{AG_KNOWLEDGE}

{context}
"""

    contents = []
    for h in history[-6:]:  # last 6 turns
        contents.append({"role": h["role"], "parts": [{"text": h["content"]}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


def _demo_response(message: str, context: str) -> str:
    """
    Demo provider — rule-based responses for common agricultural queries.
    Used when Gemini API key is not configured.
    """
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["irrigat", "water", "moisture", "पानी", "irrigation", "સિંચાઈ"]):
        return (
            "**Demo Assistant Response**\n\n"
            "Based on your farm sensor data, here's what I can tell you about irrigation:\n\n"
            "If soil moisture is below 40%, irrigation is recommended. "
            "If rain probability is above 70%, it's better to wait. "
            "Check your sensor readings in the Sensors section for current values.\n\n"
            "*For personalised advice, connect the Gemini API key in your .env file.*"
        )

    if any(w in msg_lower for w in ["disease", "blight", "fungal", "रोग", "disease", "રોગ"]):
        return (
            "**Demo Assistant Response**\n\n"
            "For disease management:\n"
            "• High humidity (>80%) increases fungal disease risk.\n"
            "• Remove and destroy infected plant material.\n"
            "• Avoid overhead irrigation — it spreads spores.\n"
            "• Use the Disease Detection page to analyse crop images.\n\n"
            "*Connect your Gemini API key for personalised disease guidance based on your farm data.*"
        )

    if any(w in msg_lower for w in ["soil", "ph", "fertilizer", "मिट्टी", "soil", "જમીન"]):
        return (
            "**Demo Assistant Response**\n\n"
            "Soil management tips:\n"
            "• Optimal pH range: 6.0–7.5 for most crops.\n"
            "• Get a soil test done every 6 months (Soil Health Card).\n"
            "• Organic matter (compost) improves soil water retention.\n\n"
            "*Connect your Gemini API key for advice based on your specific soil readings.*"
        )

    if any(w in msg_lower for w in ["crop", "plant", "harvest", "फसल", "ফসল", "પાક"]):
        return (
            "**Demo Assistant Response**\n\n"
            "Crop management guidance:\n"
            "• Monitor crops at least twice per week.\n"
            "• Record crop stages in the Crops section.\n"
            "• Flowering and Fruiting stages require consistent moisture.\n\n"
            "*Connect your Gemini API key for crop-specific advice.*"
        )

    return (
        "**Demo Assistant** (Gemini API not configured)\n\n"
        "I'm running in demo mode. I can answer basic agricultural questions but don't have "
        "access to the full AI capabilities.\n\n"
        "To enable full AI: add your GEMINI_API_KEY to the backend .env file.\n\n"
        "Ask me about: irrigation, disease, soil health, crop care, or sustainability."
    )


# ─── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    farmId: Optional[str] = None
    sessionId: Optional[str] = None
    language: str = Field(default="en", description="en | hi | gu")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(data: ChatRequest, user=Depends(get_current_user)):
    """
    Send a message to the grounded farm assistant.
    Context is built from real farm data in MongoDB.
    """
    settings = get_settings()
    db = get_database()

    # Load conversation history
    history = []
    if data.sessionId:
        session = await db.chat_sessions.find_one({"sessionId": data.sessionId, "userId": str(user["_id"])})
        if session:
            history = session.get("messages", [])

    # Build context from farm data
    context = await _build_farm_context(user["_id"], db)

    # Choose provider
    provider = "demo"
    response_text = ""

    if settings.gemini_api_key:
        try:
            response_text = await _gemini_response(data.message, context, history)
            provider = "gemini"
        except Exception as exc:
            response_text = (
                f"**Gemini API Error**: {exc}\n\n"
                + _demo_response(data.message, context)
            )
            provider = "demo_fallback"
    else:
        response_text = _demo_response(data.message, context)

    # Update conversation history
    history.append({"role": "user", "content": data.message})
    history.append({"role": "model", "content": response_text})

    # Save session
    session_id = data.sessionId or f"{user['_id']}_{int(datetime.now().timestamp())}"
    await db.chat_sessions.update_one(
        {"sessionId": session_id, "userId": str(user["_id"])},
        {"$set": {"messages": history[-20:], "updatedAt": datetime.now(timezone.utc)}},
        upsert=True,
    )

    return {
        "sessionId": session_id,
        "message": data.message,
        "response": response_text,
        "provider": provider,
        "providerLabel": "Gemini AI" if provider == "gemini" else "Demo Assistant",
        "isDemo": provider != "gemini",
        "language": data.language,
        "timestamp": datetime.now(timezone.utc),
    }


@router.get("/history")
async def chat_history(sessionId: str, user=Depends(get_current_user)):
    """Return conversation history for a session."""
    db = get_database()
    session = await db.chat_sessions.find_one(
        {"sessionId": sessionId, "userId": str(user["_id"])}
    )
    if not session:
        return {"sessionId": sessionId, "messages": []}

    return {
        "sessionId": sessionId,
        "messages": session.get("messages", []),
    }
