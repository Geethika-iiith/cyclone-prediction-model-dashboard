from prediction_pipeline import load_models, predict_rainfall
import pandas as pd
import numpy as np

models = load_models()
# Mock weather data with lots of rain/storm indicators
mock_weather = {
    "daily": {
        "time": ["2026-03-16"],
        "temperature_2m_max": [35.0],
        "temperature_2m_min": [25.0],
        "windspeed_10m_max": [80.0],
        "windgusts_10m_max": [120.0],
        "precipitation_hours": [24.0],
        "rain_sum": [50.0],
        "precipitation_sum": [55.0]
    }
}

result = predict_rainfall(models, mock_weather)
print(f"Mock Input Prediction: {result['predictions'][0]['predicted_rainfall_mm']} mm")
