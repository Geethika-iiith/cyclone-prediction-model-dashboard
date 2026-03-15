from prediction_pipeline import run_full_prediction
from api_client import fetch_weather_forecast
import traceback
import sys

# Test Kolkata
lat, lon = 22.5726, 88.3639
weather = fetch_weather_forecast(lat, lon)

try:
    predictions = run_full_prediction("Kolkata", lat, lon, weather, None)
    print("Success!")
except Exception as e:
    print(f"FAILED with {type(e).__name__}: {e}")
    traceback.print_exc(file=sys.stdout)
