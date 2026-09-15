# ─── AgriFlow AI — Irrigation Rule-Based Fallback ─────────────────────────────
"""
Rule-based smart irrigation advisor.
Used as fallback when ML model is not trained.
All rules are agronomically justified and clearly labelled as RULE-BASED.

Output:
  decision: "IRRIGATE" | "WAIT" | "REDUCE IRRIGATION"
  reason: str
  risk: "Low" | "Medium" | "High"
  estimatedWaterImpact: str
  factors: list[str]
"""


def rule_based_advice(inputs: dict) -> dict:
    """
    Applies agricultural decision rules to produce irrigation advice.
    
    Rules (in priority order):
    1. Rain probability >= 70%  → WAIT
    2. Recent rainfall >= 20mm  → WAIT (field already wet)
    3. Soil moisture >= 75%     → REDUCE IRRIGATION
    4. Rain probability >= 40% and soil moisture >= 55% → WAIT
    5. Soil moisture <= 30%     → IRRIGATE (dry soil)
    6. Soil moisture <= 45% + hot/dry conditions → IRRIGATE
    7. Default                  → WAIT (conditions adequate)
    """
    soil_moisture = inputs.get("soilMoisture", 50.0)       # % volumetric
    temperature = inputs.get("temperature", 25.0)           # °C
    humidity = inputs.get("humidity", 60.0)                 # %
    rain_prob = inputs.get("rainProbability", 0.0)          # %
    crop_type = inputs.get("cropType") or "unknown"
    growth_stage = inputs.get("growthStage") or "Vegetative"
    soil_type = inputs.get("soilType") or "Loamy"
    recent_rainfall = inputs.get("recentRainfall", 0.0)     # mm

    factors: list[str] = []
    decision = "WAIT"
    reason = ""
    risk = "Low"
    water_impact = "No change required"

    # ── Critical override: high rain probability ──────────────────────────────
    if rain_prob >= 70:
        decision = "WAIT"
        reason = f"Rain probability is {rain_prob:.0f}% — natural rainfall expected soon."
        risk = "Low"
        water_impact = "Save irrigation water — rainfall will cover demand."
        factors.append(f"High rain probability ({rain_prob:.0f}%)")

    # ── Field already wet from recent rain ───────────────────────────────────
    elif recent_rainfall >= 20:
        decision = "WAIT"
        reason = f"Recent rainfall of {recent_rainfall:.1f} mm — field is already sufficiently wet."
        risk = "Low"
        water_impact = "No irrigation needed — field moisture adequate."
        factors.append(f"Recent heavy rainfall ({recent_rainfall:.1f} mm)")

    # ── Over-irrigated / waterlogged risk ────────────────────────────────────
    elif soil_moisture >= 75:
        decision = "REDUCE IRRIGATION"
        reason = f"Soil moisture is {soil_moisture:.0f}% — above optimal range. Risk of waterlogging."
        risk = "Medium"
        water_impact = "Reduce irrigation by 50% or skip next cycle."
        factors.append(f"High soil moisture ({soil_moisture:.0f}%)")
        if soil_moisture >= 90:
            risk = "High"
            reason += " Immediate drainage may be needed."

    # ── Moderate rain likely + adequate moisture ──────────────────────────────
    elif rain_prob >= 40 and soil_moisture >= 55:
        decision = "WAIT"
        reason = (
            f"Soil moisture ({soil_moisture:.0f}%) is adequate and moderate rain ({rain_prob:.0f}%) is forecast."
        )
        risk = "Low"
        water_impact = "Monitor moisture levels and irrigate if no rain within 24 h."
        factors.append(f"Adequate moisture + rain forecast ({rain_prob:.0f}%)")

    # ── Dry soil — irrigation required ───────────────────────────────────────
    elif soil_moisture <= 30:
        decision = "IRRIGATE"
        risk = "High"
        reason = f"Soil moisture is critically low ({soil_moisture:.0f}%). Crop stress likely."
        water_impact = "Apply full irrigation cycle immediately."
        factors.append(f"Critical soil moisture ({soil_moisture:.0f}%)")
        if temperature > 35:
            factors.append(f"High temperature ({temperature:.1f}°C) — increased evapotranspiration")
            reason += f" High temperature ({temperature:.1f}°C) is accelerating moisture loss."

    # ── Mild dryness + heat ───────────────────────────────────────────────────
    elif soil_moisture <= 45 and (temperature > 30 or humidity < 40):
        decision = "IRRIGATE"
        risk = "Medium"
        reason = (
            f"Soil moisture is low ({soil_moisture:.0f}%) combined with "
            f"{'high temperature' if temperature > 30 else 'low humidity'}."
        )
        water_impact = "Apply 60–80% of standard irrigation dose."
        if temperature > 30:
            factors.append(f"High temperature ({temperature:.1f}°C)")
        if humidity < 40:
            factors.append(f"Low humidity ({humidity:.0f}%)")
        factors.append(f"Soil moisture borderline ({soil_moisture:.0f}%)")

    # ── Default: adequate conditions ──────────────────────────────────────────
    else:
        decision = "WAIT"
        risk = "Low"
        reason = f"Soil moisture ({soil_moisture:.0f}%) is within acceptable range. No immediate irrigation needed."
        water_impact = "Monitor over next 12–24 hours."
        factors.append(f"Adequate soil moisture ({soil_moisture:.0f}%)")

    # ── Crop-stage modifier (advisory only) ───────────────────────────────────
    stage_notes = {
        "Flowering": "⚠ Flowering stage — maintain consistent soil moisture to prevent flower drop.",
        "Fruiting": "⚠ Fruiting stage — avoid water stress to ensure uniform fruit development.",
        "Germination": "Germination stage — keep soil moist but not waterlogged.",
    }
    if growth_stage in stage_notes:
        factors.append(stage_notes[growth_stage])

    # ── Sandy soil modifier ───────────────────────────────────────────────────
    if soil_type in ("Sandy", "Sandy Loam") and decision == "WAIT" and soil_moisture <= 50:
        factors.append(f"Sandy soil drains quickly — monitor moisture closely.")

    return {
        "decision": decision,
        "reason": reason,
        "risk": risk,
        "estimatedWaterImpact": water_impact,
        "factors": factors,
        "inputs": {
            "soilMoisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "rainProbability": rain_prob,
            "cropType": crop_type,
            "growthStage": growth_stage,
            "soilType": soil_type,
            "recentRainfall": recent_rainfall,
        },
    }
