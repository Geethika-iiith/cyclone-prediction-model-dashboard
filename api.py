from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pandas as pd

from api_client import (
    fetch_weather_forecast,
    fetch_shelters_osm,
    get_simulated_active_cyclone,
    geocode_city
)
from prediction_pipeline import run_full_prediction, load_models

app = FastAPI(title="CycloneGuard API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_city_database():
    base = os.path.dirname(os.path.abspath(__file__))
    cities_file = os.path.join(base, "data_cities_expanded.csv")
    if os.path.exists(cities_file):
        return pd.read_csv(cities_file)
    return pd.DataFrame({
        "city": ["Mumbai", "Chennai", "Visakhapatnam", "Kolkata", "Bhubaneswar"],
        "latitude": [19.076, 13.0827, 17.6868, 22.5726, 20.2961],
        "longitude": [72.8777, 80.2707, 83.2185, 88.3639, 85.8245],
        "population_density": [31700, 26553, 18480, 24306, 6228],
    })

@app.get("/api/cities")
def get_cities():
    df = get_city_database()
    cities = []
    for _, row in df.iterrows():
        cities.append({
            "city": row["city"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "population_density": row.get("population_density", 10000)
        })
    return {"cities": cities}

@app.get("/api/search")
def search_city(q: str):
    geo = geocode_city(q)
    if geo:
        return geo
    raise HTTPException(status_code=404, detail="City not found")

@app.get("/api/predict")
def predict_disaster(city: str, lat: float, lon: float, pop_density: float = 10000, sim: bool = True):
    try:
        weather_data = fetch_weather_forecast(lat, lon, days=7)
        
        cyclone_data = None
        if sim:
            cyclone_data = get_simulated_active_cyclone(lat, lon)
            
        predictions = run_full_prediction(
            city_name=city,
            city_lat=lat,
            city_lon=lon,
            weather_data=weather_data,
            cyclone_data=cyclone_data if cyclone_data else {
                "wind_kmh": 0, "pressure_mb": 1013,
                "lat": lat, "lon": lon,
                "distance_km": 9999, "track": [],
            },
            population_density=pop_density,
        )
        
        shelters = fetch_shelters_osm(lat, lon, radius_km=20)
        
        return {
            "predictions": predictions,
            "weather": weather_data,
            "cyclone": cyclone_data,
            "shelters": shelters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
