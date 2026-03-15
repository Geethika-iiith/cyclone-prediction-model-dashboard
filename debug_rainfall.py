from prediction_pipeline import run_full_prediction, load_models, predict_rainfall
from api_client import fetch_weather_forecast, get_simulated_active_cyclone
import json
import pandas as pd
import numpy as np

# Test Mumbai
lat, lon = 19.076, 72.8777
weather = fetch_weather_forecast(lat, lon)
print("--- Weather Data Info ---")
if weather:
    print(f"Current Temp: {weather.get('current_weather', {}).get('temperature')}")
    print(f"Daily Rain Sum: {weather.get('daily', {}).get('rain_sum')}")
else:
    print("Weather data is NONE")

models = load_models()
if "rainfall" not in models:
    print("RAINFALL MODEL NOT LOADED")
else:
    meta = models["rainfall_meta"]
    print(f"Rainfall Model Features: {meta['features']}")
    
    # Run predict_rainfall directly to see intermediate values
    daily = weather.get("daily", {})
    dates = daily.get("time", [])
    
    for i, date in enumerate(dates[:3]): # Just first 3 days
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
            "rain_lag_3d": 0, # simplified for debug
            "rain_lag_7d": 0, # simplified for debug
            "wind_change": 0, # simplified for debug
            "temp_change": 0, # simplified for debug
            "month": 3,
            "is_cyclone_season": 0,
        }
        X = pd.DataFrame([row])[meta["features"]]
        pred = models["rainfall"].predict(X)[0]
        print(f"Date: {date}, Features: {row}, Raw Pred: {pred}")

predictions = run_full_prediction("Mumbai", lat, lon, weather, None)
print(f"Final Prediction result: {predictions['rainfall']['predictions'][0]}")
