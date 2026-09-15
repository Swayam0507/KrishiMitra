# ─── AgriFlow AI — Sensor Anomaly Detection ───────────────────────────────────
"""
Detects abnormal sensor readings using:
  1. Physical bounds check (unrealistic values)
  2. Z-score statistical anomaly (vs. recent window)
  3. Sudden change detection (rate-of-change)
  4. Inactivity detection

Severity levels:
  Normal   — reading within expected range
  Warning  — moderate anomaly, monitor closely
  Critical — severe anomaly, immediate attention needed
"""
import math
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId

from ..database import get_database
from ..dependencies import get_current_user

router = APIRouter()

# ─── Physical bounds (outside = unrealistic) ──────────────────────────────────
BOUNDS = {
    "soilMoisture":  (0.0,  100.0),
    "temperature":   (-10.0, 55.0),
    "humidity":      (0.0,  100.0),
    "soilPH":        (3.0,  10.0),
}

# ─── Warning and critical thresholds ─────────────────────────────────────────
THRESHOLDS = {
    "soilMoisture":  {"warning_low": 15, "critical_low": 8,  "warning_high": 88, "critical_high": 95},
    "temperature":   {"warning_low": 5,  "critical_low": 0,  "warning_high": 42, "critical_high": 48},
    "humidity":      {"warning_low": 15, "critical_low": 8,  "warning_high": 95, "critical_high": 99},
    "soilPH":        {"warning_low": 4.5,"critical_low": 4.0,"warning_high": 8.5,"critical_high": 9.0},
}

# ─── Statistical helpers ───────────────────────────────────────────────────────

def _mean_std(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        return (values[0] if values else 0.0), 0.0
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    return mean, math.sqrt(variance)


def _z_score(value: float, mean: float, std: float) -> Optional[float]:
    if std == 0:
        return None
    return abs((value - mean) / std)


def _analyze_sensor(
    metric: str,
    current: float,
    history: list[float],
    previous: Optional[float],
) -> dict:
    """
    Returns:
      severity: "Normal" | "Warning" | "Critical"
      anomalyType: str
      details: str
    """
    low, high = BOUNDS[metric]
    thr = THRESHOLDS[metric]
    severity = "Normal"
    anomaly_type = None
    details = f"{metric} = {current:.2f}"

    # 1. Physical bounds
    if current < low or current > high:
        return {
            "severity": "Critical",
            "anomalyType": "Unrealistic Value",
            "details": f"{metric} = {current:.2f} is outside physical range [{low}, {high}]",
        }

    # 2. Threshold checks
    if current <= thr["critical_low"]:
        severity, anomaly_type = "Critical", "Critically Low Value"
        details = f"{metric} = {current:.2f} — critically below minimum threshold {thr['critical_low']}"
    elif current >= thr["critical_high"]:
        severity, anomaly_type = "Critical", "Critically High Value"
        details = f"{metric} = {current:.2f} — critically above maximum threshold {thr['critical_high']}"
    elif current <= thr["warning_low"]:
        severity, anomaly_type = "Warning", "Low Value"
        details = f"{metric} = {current:.2f} — below warning threshold {thr['warning_low']}"
    elif current >= thr["warning_high"]:
        severity, anomaly_type = "Warning", "High Value"
        details = f"{metric} = {current:.2f} — above warning threshold {thr['warning_high']}"

    # 3. Z-score statistical anomaly (only if we have enough history)
    if len(history) >= 5:
        mean, std = _mean_std(history)
        z = _z_score(current, mean, std)
        if z is not None:
            if z > 3.5 and severity == "Normal":
                severity = "Critical"
                anomaly_type = "Statistical Outlier"
                details = f"{metric} = {current:.2f} — Z-score {z:.1f} (extreme statistical outlier vs. last {len(history)} readings, mean={mean:.2f})"
            elif z > 2.5 and severity == "Normal":
                severity = "Warning"
                anomaly_type = "Statistical Anomaly"
                details = f"{metric} = {current:.2f} — Z-score {z:.1f} (anomaly vs. recent readings, mean={mean:.2f})"

    # 4. Sudden change detection
    if previous is not None:
        delta = abs(current - previous)
        sudden_change_thresholds = {
            "soilMoisture": 20,
            "temperature": 8,
            "humidity": 25,
            "soilPH": 1.5,
        }
        if delta > sudden_change_thresholds.get(metric, 999):
            if severity == "Normal":
                severity = "Warning"
            anomaly_type = "Sudden Change"
            details += f" — sudden change of {delta:.2f} from previous reading ({previous:.2f})"

    return {
        "severity": severity,
        "anomalyType": anomaly_type,
        "details": details,
    }


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/analyze/{farm_id}")
async def analyze_sensor_anomalies(
    farm_id: str,
    window: int = Query(default=20, ge=5, le=100, description="Number of past readings for baseline"),
    user=Depends(get_current_user),
):
    """
    Analyze the latest sensor reading against recent history for anomalies.
    Returns per-metric anomaly report + overall farm sensor health.
    """
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(farm_id), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Fetch recent readings
    readings = await db.sensor_readings.find(
        {"farmId": farm_id}
    ).sort("timestamp", -1).limit(window + 1).to_list(window + 1)

    if not readings:
        return {
            "farmId": farm_id,
            "status": "No sensor data",
            "anomalies": [],
            "overallHealth": "Unknown",
            "inactivityAlert": None,
        }

    latest = readings[0]
    history_docs = readings[1:]  # previous readings

    # Inactivity check
    now = datetime.now(timezone.utc)
    latest_ts = latest["timestamp"]
    if latest_ts.tzinfo is None:
        latest_ts = latest_ts.replace(tzinfo=timezone.utc)
    minutes_since = (now - latest_ts).total_seconds() / 60

    inactivity_alert = None
    if minutes_since > 60:
        inactivity_alert = {
            "severity": "Warning" if minutes_since < 120 else "Critical",
            "message": f"No sensor data for {minutes_since:.0f} minutes — sensor may be offline.",
        }

    # Analyze each metric
    metrics = ["soilMoisture", "temperature", "humidity", "soilPH"]
    anomalies = []

    for metric in metrics:
        if metric not in latest:
            continue

        current = latest[metric]
        previous = history_docs[0].get(metric) if history_docs else None
        history_vals = [d[metric] for d in history_docs if metric in d]

        analysis = _analyze_sensor(metric, current, history_vals, previous)

        anomalies.append({
            "metric": metric,
            "currentValue": current,
            "unit": _metric_unit(metric),
            **analysis,
        })

    # Overall health = worst severity
    severities = [a["severity"] for a in anomalies]
    if "Critical" in severities:
        overall = "Critical"
    elif "Warning" in severities:
        overall = "Warning"
    else:
        overall = "Normal"

    # Save anomaly report
    report = {
        "farmId": farm_id,
        "userId": str(user["_id"]),
        "overallHealth": overall,
        "anomalies": anomalies,
        "latestReadingId": str(latest["_id"]),
        "timestamp": now,
        "dataSource": "SIMULATED SENSOR",
    }
    await db.anomaly_reports.insert_one(report)

    return {
        "farmId": farm_id,
        "overallHealth": overall,
        "anomalies": anomalies,
        "latestReading": {
            k: v for k, v in latest.items()
            if k in ["soilMoisture", "temperature", "humidity", "soilPH", "timestamp"]
        },
        "inactivityAlert": inactivity_alert,
        "dataSource": "SIMULATED SENSOR",
        "timestamp": now,
    }


def _metric_unit(metric: str) -> str:
    return {"soilMoisture": "%", "temperature": "°C", "humidity": "%", "soilPH": "pH"}.get(metric, "")


@router.get("/history/{farm_id}")
async def anomaly_history(
    farm_id: str,
    limit: int = Query(default=20, le=100),
    user=Depends(get_current_user),
):
    """Return past anomaly reports for a farm."""
    db = get_database()
    farm = await db.farms.find_one({"_id": ObjectId(farm_id), "ownerId": user["_id"]})
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    docs = await db.anomaly_reports.find(
        {"farmId": farm_id}
    ).sort("timestamp", -1).limit(limit).to_list(limit)

    return [
        {
            "id": str(d["_id"]),
            "overallHealth": d["overallHealth"],
            "criticalCount": sum(1 for a in d.get("anomalies", []) if a["severity"] == "Critical"),
            "warningCount":  sum(1 for a in d.get("anomalies", []) if a["severity"] == "Warning"),
            "timestamp": d["timestamp"],
        }
        for d in docs
    ]
