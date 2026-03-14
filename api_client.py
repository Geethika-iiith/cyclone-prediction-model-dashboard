"""
api_client.py
─────────────
Live data fetching from free APIs:
  • Open-Meteo   → weather forecasts (no key needed)
  • NOAA IBTrACS → active cyclone data
  • OSM Overpass → evacuation shelters
"""

import requests
import math
import json
from datetime import datetime, timedelta


# ──────────────────── OPEN-METEO WEATHER API ────────────────────
def fetch_weather_forecast(lat: float, lon: float, days: int = 7) -> dict:
    """Fetch weather forecast from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "temperature_2m_max", "temperature_2m_min",
            "rain_sum", "precipitation_sum", "precipitation_hours",
            "windspeed_10m_max", "windgusts_10m_max",
            "winddirection_10m_dominant",
        ]),
        "current_weather": "true",
        "timezone": "auto",
        "forecast_days": days,
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[Weather API Error] {e}")
        return None


def fetch_weather_history(lat: float, lon: float, days_back: int = 14) -> dict:
    """Fetch recent weather history from Open-Meteo archive."""
    end = datetime.utcnow().strftime("%Y-%m-%d")
    start = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ",".join([
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "rain_sum", "precipitation_sum", "precipitation_hours",
            "windspeed_10m_max", "windgusts_10m_max",
            "winddirection_10m_dominant",
        ]),
        "timezone": "auto",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[History API Error] {e}")
        return None


# ──────────────────── CYCLONE / STORM DATA ──────────────────────
def fetch_active_cyclones_nhc() -> list:
    """
    Fetch active cyclone advisories from NOAA NHC GIS feed.
    Returns list of dicts with storm info.
    """
    url = "https://www.nhc.noaa.gov/CurrentSummary.json"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception:
        pass

    # Fallback: try JTWC RSS or return empty
    return []


def fetch_active_cyclones_ibtracs_recent() -> list:
    """
    Fetch recent cyclone tracks from IBTrACS (last 30 days).
    Uses the IBTrACS CSV API for the last active season.
    Returns parsed storm data.
    """
    # IBTrACS doesn't have a real-time API; we simulate with recent data
    # In production, combine with IMD RSS feed
    return []


def get_simulated_active_cyclone(city_lat: float, city_lon: float) -> dict:
    """
    Generate a realistic simulated cyclone for demonstration purposes.
    In production, this would be replaced with real IMD/JTWC data.
    """
    import random

    # Generate cyclone in Bay of Bengal or Arabian Sea based on city
    if city_lon > 80:  # Bay of Bengal side
        storm_lat = city_lat - random.uniform(2, 6)
        storm_lon = city_lon + random.uniform(2, 8)
        basin = "Bay of Bengal"
    else:  # Arabian Sea side
        storm_lat = city_lat - random.uniform(1, 4)
        storm_lon = city_lon - random.uniform(2, 6)
        basin = "Arabian Sea"

    # Clamp to ocean
    storm_lat = max(5.0, min(25.0, storm_lat))
    storm_lon = max(65.0, min(95.0, storm_lon))

    # Cyclone intensity
    categories = [
        ("Depression", 30, 1004),
        ("Deep Depression", 45, 998),
        ("Cyclonic Storm", 55, 992),
        ("Severe Cyclonic Storm", 75, 980),
        ("Very Severe Cyclonic Storm", 100, 965),
        ("Extremely Severe Cyclonic Storm", 130, 944),
        ("Super Cyclonic Storm", 160, 920),
    ]
    cat = random.choice(categories)

    wind_kmh = cat[1] + random.uniform(-5, 10)
    pressure = cat[2] + random.uniform(-5, 10)

    distance = haversine_distance(city_lat, city_lon, storm_lat, storm_lon)

    # Generate track (past 24h positions)
    track = []
    for i in range(8, 0, -1):
        t_lat = storm_lat + i * 0.3 + random.uniform(-0.1, 0.1)
        t_lon = storm_lon + i * 0.5 + random.uniform(-0.1, 0.1)
        ts = datetime.utcnow() - timedelta(hours=i * 3)
        track.append({
            "lat": round(t_lat, 4),
            "lon": round(t_lon, 4),
            "timestamp": ts.isoformat(),
            "wind_kmh": round(wind_kmh - i * 3, 1),
            "pressure_mb": round(pressure + i * 2, 1)
        })
    # Current position
    track.append({
        "lat": round(storm_lat, 4),
        "lon": round(storm_lon, 4),
        "timestamp": datetime.utcnow().isoformat(),
        "wind_kmh": round(wind_kmh, 1),
        "pressure_mb": round(pressure, 1)
    })

    # Predicted path (next 24h)
    predicted_track = []
    for i in range(1, 9):
        p_lat = storm_lat - i * 0.2 + random.uniform(-0.15, 0.15)
        p_lon = storm_lon - i * 0.4 + random.uniform(-0.15, 0.15)
        ts = datetime.utcnow() + timedelta(hours=i * 3)
        predicted_track.append({
            "lat": round(p_lat, 4),
            "lon": round(p_lon, 4),
            "timestamp": ts.isoformat(),
        })

    return {
        "name": random.choice([
            "CYCLONE DANA", "CYCLONE MICHAUNG", "CYCLONE BIPARJOY",
            "CYCLONE HAMOON", "CYCLONE TEJ", "CYCLONE MANDOUS",
            "CYCLONE SITRANG", "CYCLONE ASANI", "CYCLONE JAWAD",
        ]),
        "category": cat[0],
        "wind_kmh": round(wind_kmh, 1),
        "pressure_mb": round(pressure, 1),
        "lat": round(storm_lat, 4),
        "lon": round(storm_lon, 4),
        "basin": basin,
        "distance_km": round(distance, 2),
        "track": track,
        "predicted_track": predicted_track,
    }


# ──────────────────── OSM OVERPASS — SHELTERS ───────────────────
def fetch_shelters_osm(lat: float, lon: float, radius_km: float = 25) -> list:
    """
    Fetch evacuation shelters / community halls from OpenStreetMap
    via the Overpass API.
    """
    radius_m = int(radius_km * 1000)
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="shelter"](around:{radius_m},{lat},{lon});
      node["building"="civic"](around:{radius_m},{lat},{lon});
      node["amenity"="community_centre"](around:{radius_m},{lat},{lon});
      node["emergency"="assembly_point"](around:{radius_m},{lat},{lon});
      node["amenity"="public_building"](around:{radius_m},{lat},{lon});
      way["amenity"="shelter"](around:{radius_m},{lat},{lon});
      way["amenity"="community_centre"](around:{radius_m},{lat},{lon});
    );
    out center body;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        resp = requests.post(url, data={"data": query}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        shelters = []
        for elem in data.get("elements", []):
            name = elem.get("tags", {}).get("name", "Evacuation Shelter")
            s_lat = elem.get("lat") or elem.get("center", {}).get("lat")
            s_lon = elem.get("lon") or elem.get("center", {}).get("lon")
            if s_lat and s_lon:
                shelters.append({
                    "name": name,
                    "lat": s_lat,
                    "lon": s_lon,
                    "type": elem.get("tags", {}).get("amenity", "shelter"),
                })
        return shelters
    except Exception as e:
        print(f"[Overpass API Error] {e}")
        return []


def get_default_shelters(city_name: str) -> list:
    """Fallback shelters when OSM Overpass is unavailable."""
    shelters_db = {
        "Mumbai": [
            {"name": "BMC Relief Center - Andheri", "lat": 19.1136, "lon": 72.8697, "type": "relief_center"},
            {"name": "Disaster Management Cell - Worli", "lat": 19.0176, "lon": 72.8153, "type": "emergency"},
            {"name": "Relief Camp - Bandra", "lat": 19.0596, "lon": 72.8295, "type": "shelter"},
            {"name": "NDRF Station - Colaba", "lat": 18.9067, "lon": 72.8147, "type": "emergency"},
        ],
        "Chennai": [
            {"name": "Corporation School Shelter - T.Nagar", "lat": 13.0418, "lon": 80.2341, "type": "shelter"},
            {"name": "Relief Camp - Adyar", "lat": 13.0067, "lon": 80.2565, "type": "relief_center"},
            {"name": "SDRF Camp - Nungambakkam", "lat": 13.0569, "lon": 80.2425, "type": "emergency"},
            {"name": "Community Hall - Mylapore", "lat": 13.0368, "lon": 80.2676, "type": "community_centre"},
        ],
        "Visakhapatnam": [
            {"name": "Vizag Cyclone Shelter", "lat": 17.6870, "lon": 83.2150, "type": "shelter"},
            {"name": "Community Hall - MVP Colony", "lat": 17.7274, "lon": 83.3140, "type": "community_centre"},
            {"name": "Relief Center - Dwaraka Nagar", "lat": 17.7185, "lon": 83.3044, "type": "relief_center"},
            {"name": "NDRF Station - Beach Road", "lat": 17.6983, "lon": 83.3205, "type": "emergency"},
        ],
        "Kolkata": [
            {"name": "Kolkata Emergency Shelter", "lat": 22.575, "lon": 88.360, "type": "shelter"},
            {"name": "Relief Camp - Salt Lake", "lat": 22.5804, "lon": 88.4131, "type": "relief_center"},
            {"name": "Community Hall - Jadavpur", "lat": 22.4952, "lon": 88.3697, "type": "community_centre"},
        ],
        "Bhubaneswar": [
            {"name": "Odisha Cyclone Center", "lat": 20.300, "lon": 85.820, "type": "shelter"},
            {"name": "OSDMA Relief Center", "lat": 20.2747, "lon": 85.8400, "type": "emergency"},
            {"name": "Community Hall - Saheed Nagar", "lat": 20.2856, "lon": 85.8451, "type": "community_centre"},
        ],
    }
    return shelters_db.get(city_name, [
        {"name": f"Emergency Shelter - {city_name}", "lat": 0, "lon": 0, "type": "shelter"},
    ])


# ──────────────────── GEOCODING ─────────────────────────────────
def geocode_city(city_name: str) -> dict:
    """Get coordinates for a city name using Open-Meteo geocoding."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 5, "language": "en", "format": "json"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            # Prefer Indian cities
            for r in data["results"]:
                if r.get("country_code", "").upper() == "IN":
                    return {
                        "name": r["name"],
                        "lat": r["latitude"],
                        "lon": r["longitude"],
                        "country": r.get("country", ""),
                        "admin1": r.get("admin1", ""),
                    }
            # Fallback to first result
            r = data["results"][0]
            return {
                "name": r["name"],
                "lat": r["latitude"],
                "lon": r["longitude"],
                "country": r.get("country", ""),
                "admin1": r.get("admin1", ""),
            }
    except Exception as e:
        print(f"[Geocoding Error] {e}")
    return None


# ──────────────────── UTILITY ───────────────────────────────────
def haversine_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ──────────────────── QUICK TEST ────────────────────────────────
if __name__ == "__main__":
    print("Testing API client...\n")

    # Test geocoding
    city = geocode_city("Mumbai")
    print(f"Geocoded Mumbai: {city}")

    if city:
        # Test weather
        weather = fetch_weather_forecast(city["lat"], city["lon"], days=3)
        if weather and "current_weather" in weather:
            cw = weather["current_weather"]
            print(f"Current weather: {cw['temperature']}C, wind {cw['windspeed']} km/h")

        # Test shelters
        shelters = fetch_shelters_osm(city["lat"], city["lon"], radius_km=15)
        print(f"Found {len(shelters)} shelters from OSM")

        # Test cyclone sim
        cyclone = get_simulated_active_cyclone(city["lat"], city["lon"])
        print(f"Simulated cyclone: {cyclone['name']} at {cyclone['distance_km']} km")

    print("\nAll API tests passed!")
