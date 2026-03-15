"""
prediction_pipeline.py
──────────────────────
End-to-end prediction pipeline:
  City input → Fetch data → Preprocess → Run ML models → Return predictions
"""

import os
import pickle
import math
import numpy as np
import pandas as pd
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = BASE


def _load_model(name):
    # Prefer the structured models/ folder, then fall back to legacy root layout.
    candidate_paths = [
        os.path.join(MODELS_DIR, name),
        os.path.join(BASE, name),
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)

    searched = ", ".join(candidate_paths)
    raise FileNotFoundError(f"{name} not found in: {searched}")


# ──────────────────── LOAD ALL MODELS ───────────────────────────
def load_models():
    models = {}
    try:
        models["rainfall"] = _load_model("rainfall_model.pkl")
        models["rainfall_meta"] = _load_model("rainfall_model_meta.pkl")
    except Exception as e:
        print(f"Warning: Could not load rainfall model: {e}")

    try:
        models["wind"] = _load_model("wind_model.pkl")
        models["wind_meta"] = _load_model("wind_model_meta.pkl")
    except Exception as e:
        print(f"Warning: Could not load wind model: {e}")

    try:
        models["risk"] = _load_model("risk_classifier.pkl")
        models["risk_encoder"] = _load_model("risk_label_encoder.pkl")
    except Exception as e:
        print(f"Warning: Could not load risk model: {e}")

    try:
        models["path_meta"] = _load_model("path_prediction.pkl")
    except Exception as e:
        print(f"Warning: Could not load path prediction: {e}")

    return models


# ──────────────────── RAINFALL PREDICTION ───────────────────────
def predict_rainfall(models: dict, weather_data: dict) -> dict:
    """
    Predict rainfall intensity from weather features.
    Input: weather forecast data from Open-Meteo
    Output: predicted rainfall (mm) for each forecast day
    """
    if "rainfall" not in models or weather_data is None:
        return {"predictions": [], "model_r2": 0}

    meta = models["rainfall_meta"]
    model = models["rainfall"]
    features = meta["features"]

    daily = weather_data.get("daily", {})
    dates = daily.get("time", [])

    predictions = []
    for i, date in enumerate(dates):
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            month = dt.month
            is_cyclone_season = 1 if month in [4, 5, 6, 10, 11, 12] else 0

            # Build feature vector
            row = {
                "temperature_2m_mean": (
                    (daily.get("temperature_2m_max", [0])[i] or 0) +
                    (daily.get("temperature_2m_min", [0])[i] or 0)
                ) / 2,
                "temperature_2m_max": daily.get("temperature_2m_max", [0])[i] or 0,
                "temperature_2m_min": daily.get("temperature_2m_min", [0])[i] or 0,
                "windspeed_10m_max": daily.get("windspeed_10m_max", [0])[i] or 0,
                "windgusts_10m_max": daily.get("windgusts_10m_max", [0])[i] or 0,
                "precipitation_hours": daily.get("precipitation_hours", [0])[i] or 0,
                "rain_lag_1d": daily.get("rain_sum", [0])[max(0, i - 1)] or 0,
                "rain_lag_3d": sum(
                    (daily.get("rain_sum", [0])[max(0, j)] or 0)
                    for j in range(max(0, i - 3), i)
                ) / max(1, min(3, i)),
                "rain_lag_7d": sum(
                    (daily.get("rain_sum", [0])[max(0, j)] or 0)
                    for j in range(max(0, i - 7), i)
                ) / max(1, min(7, i)),
                "wind_change": (
                    (daily.get("windspeed_10m_max", [0])[i] or 0) -
                    (daily.get("windspeed_10m_max", [0])[max(0, i - 1)] or 0)
                ),
                "temp_change": (
                    ((daily.get("temperature_2m_max", [0])[i] or 0) +
                     (daily.get("temperature_2m_min", [0])[i] or 0)) / 2 -
                    ((daily.get("temperature_2m_max", [0])[max(0, i - 1)] or 0) +
                     (daily.get("temperature_2m_min", [0])[max(0, i - 1)] or 0)) / 2
                ),
                "month": month,
                "is_cyclone_season": is_cyclone_season,
            }

            X = pd.DataFrame([row])[features]
            pred = float(model.predict(X)[0])
            pred = max(0, pred)  # No negative rainfall

            predictions.append({
                "date": date,
                "predicted_rainfall_mm": round(pred, 2),
                "actual_rain_sum": daily.get("rain_sum", [None])[i],
            })
        except Exception as e:
            predictions.append({
                "date": date,
                "predicted_rainfall_mm": 0,
                "actual_rain_sum": daily.get("rain_sum", [None])[i],
                "error": str(e),
            })

    return {
        "predictions": predictions,
        "model_r2": meta.get("r2", 0),
        "model_rmse": meta.get("rmse", 0),
    }


# ──────────────────── WIND SPEED PREDICTION ─────────────────────
def predict_wind_speed(models: dict, cyclone_data: dict) -> dict:
    """
    Predict wind speed from cyclone features.
    Input: cyclone data dict
    Output: predicted wind speed (km/h)
    """
    if "wind" not in models or cyclone_data is None:
        return {"predicted_wind_kmh": 0, "model_r2": 0}

    meta = models["wind_meta"]
    model = models["wind"]
    features = meta["features"]

    # Map cyclone category to number
    cat_map = {
        "Depression": 1, "Deep Depression": 2,
        "Cyclonic Storm": 3, "Severe Cyclonic Storm": 4,
        "Very Severe Cyclonic Storm": 5,
        "Extremely Severe Cyclonic Storm": 6,
        "Super Cyclonic Storm": 7,
    }

    track = cyclone_data.get("track", [])
    current = track[-1] if track else {}
    prev = track[-2] if len(track) >= 2 else current

    row = {
        "pressure_mb": cyclone_data.get("pressure_mb", 1000),
        "pressure_change": (
            current.get("pressure_mb", 1000) - prev.get("pressure_mb", 1000)
        ),
        "category_num": cat_map.get(cyclone_data.get("category", ""), 3),
        "LAT": cyclone_data.get("lat", 15),
        "LON": cyclone_data.get("lon", 85),
        "lat_change": (
            current.get("lat", 15) - prev.get("lat", 15)
        ),
        "lon_change": (
            current.get("lon", 85) - prev.get("lon", 85)
        ),
        "month": datetime.utcnow().month,
        "dist_to_land_km": cyclone_data.get("distance_km", 500) * 0.5,
    }

    X = pd.DataFrame([row])[features]
    pred = float(model.predict(X)[0])
    pred = max(0, pred)

    return {
        "predicted_wind_kmh": round(pred, 1),
        "model_r2": meta.get("r2", 0),
        "model_rmse": meta.get("rmse", 0),
    }


# ──────────────────── CYCLONE PATH PREDICTION ───────────────────
def predict_cyclone_path(cyclone_data: dict, city_lat: float, city_lon: float) -> dict:
    """
    Predict cyclone movement using linear extrapolation.
    Uses last N track positions to estimate future positions.
    """
    track = cyclone_data.get("track", [])
    if len(track) < 2:
        return {
            "predicted_positions": [],
            "predicted_distances": [],
            "method": "linear_extrapolation",
        }

    # Use last 4 positions for extrapolation
    lookback = min(4, len(track))
    recent = track[-lookback:]

    # Calculate average movement per step
    lat_changes = []
    lon_changes = []
    for i in range(1, len(recent)):
        lat_changes.append(recent[i]["lat"] - recent[i - 1]["lat"])
        lon_changes.append(recent[i]["lon"] - recent[i - 1]["lon"])

    avg_dlat = np.mean(lat_changes)
    avg_dlon = np.mean(lon_changes)

    # Predict next 8 steps (24 hours at 3hr intervals)
    current_lat = track[-1]["lat"]
    current_lon = track[-1]["lon"]

    predicted = []
    distances = []
    for step in range(1, 9):
        pred_lat = current_lat + avg_dlat * step
        pred_lon = current_lon + avg_dlon * step

        dist = haversine_distance(city_lat, city_lon, pred_lat, pred_lon)

        from datetime import timedelta
        ts = datetime.utcnow() + timedelta(hours=step * 3)

        predicted.append({
            "lat": round(pred_lat, 4),
            "lon": round(pred_lon, 4),
            "timestamp": ts.isoformat(),
            "hours_ahead": step * 3,
        })
        distances.append(round(dist, 2))

    return {
        "predicted_positions": predicted,
        "predicted_distances": distances,
        "closest_approach_km": min(distances) if distances else 9999,
        "closest_approach_hours": (distances.index(min(distances)) + 1) * 3 if distances else 0,
        "method": "linear_extrapolation",
    }


# ──────────────────── RISK CLASSIFICATION ───────────────────────
def predict_risk_level(
    models: dict,
    wind_kmh: float,
    rainfall_mm: float,
    distance_km: float,
    population_density: float = 10000,
) -> dict:
    """
    Classify disaster risk level.
    Input: predicted wind, rainfall, distance, population density
    Output: risk category (Severe/High/Medium/Low)
    """
    if "risk" not in models:
        # Fallback rule-based classification
        if wind_kmh > 120 or (distance_km < 100 and wind_kmh > 80):
            return {"risk_level": "Severe", "confidence": 0.85}
        elif wind_kmh > 80 or distance_km < 200:
            return {"risk_level": "High", "confidence": 0.80}
        elif wind_kmh > 50 or distance_km < 400:
            return {"risk_level": "Medium", "confidence": 0.75}
        else:
            return {"risk_level": "Low", "confidence": 0.70}

    model = models["risk"]
    encoder = models["risk_encoder"]

    # Model features: wind_kmh, pressure_mb, distance_km, population_density
    # We estimate pressure from wind speed when not available
    estimated_pressure = max(900, 1013 - (wind_kmh * 0.6))

    row = {
        "wind_kmh": wind_kmh,
        "pressure_mb": estimated_pressure,
        "distance_km": distance_km,
        "population_density": population_density,
    }

    X = pd.DataFrame([row])
    pred_encoded = model.predict(X)[0]
    risk_label = encoder.inverse_transform([pred_encoded])[0]

    # Get probabilities
    proba = model.predict_proba(X)[0]
    confidence = float(max(proba))

    return {
        "risk_level": risk_label,
        "confidence": round(confidence, 3),
        "probabilities": {
            encoder.inverse_transform([i])[0]: round(float(p), 3)
            for i, p in enumerate(proba)
        },
    }


# ──────────────────── FULL PIPELINE ─────────────────────────────
def run_full_prediction(
    city_name: str,
    city_lat: float,
    city_lon: float,
    weather_data: dict,
    cyclone_data: dict,
    population_density: float = 10000,
) -> dict:
    """
    Complete prediction pipeline:
    City → Weather + Cyclone data → ML models → Risk assessment
    """
    models = load_models()

    # 1. Rainfall prediction
    rainfall_result = predict_rainfall(models, weather_data)
    avg_rainfall = 0
    if rainfall_result["predictions"]:
        avg_rainfall = np.mean([
            p["predicted_rainfall_mm"]
            for p in rainfall_result["predictions"]
        ])

    # 2. Wind speed prediction
    wind_result = predict_wind_speed(models, cyclone_data)

    # 3. Cyclone path prediction
    path_result = predict_cyclone_path(cyclone_data, city_lat, city_lon)

    # 4. Risk classification
    distance = cyclone_data.get("distance_km", 9999)
    risk_result = predict_risk_level(
        models,
        wind_kmh=max(wind_result["predicted_wind_kmh"], cyclone_data.get("wind_kmh", 0)),
        rainfall_mm=avg_rainfall,
        distance_km=distance,
        population_density=population_density,
    )

    return {
        "city": city_name,
        "coordinates": {"lat": city_lat, "lon": city_lon},
        "rainfall": rainfall_result,
        "wind": wind_result,
        "cyclone_path": path_result,
        "risk": risk_result,
        "cyclone": cyclone_data,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ──────────────────── UTILITY ───────────────────────────────────
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


if __name__ == "__main__":
    models = load_models()
    print("Loaded models:", list(models.keys()))
    print("Rainfall features:", models.get("rainfall_meta", {}).get("features", []))
    print("Wind features:", models.get("wind_meta", {}).get("features", []))
