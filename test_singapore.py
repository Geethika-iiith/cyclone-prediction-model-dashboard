from prediction_pipeline import run_full_prediction
from api_client import fetch_weather_forecast
import numpy as np

# Test Singapore (Latitude: 1.3521, Longitude: 103.8198) - likely to have rain
lat, lon = 1.3521, 103.8198
weather = fetch_weather_forecast(lat, lon)

if weather and "daily" in weather:
    print(f"API Rain Sum: {weather['daily'].get('rain_sum')}")
    print(f"API Precip Hours: {weather['daily'].get('precipitation_hours')}")

predictions = run_full_prediction("Singapore", lat, lon, weather, None)
rain_preds = [p['predicted_rainfall_mm'] for p in predictions['rainfall']['predictions']]
print(f"Rainfall Predictions: {rain_preds}")
print(f"Avg Rain: {np.mean(rain_preds) if rain_preds else 0}")
