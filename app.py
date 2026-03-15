"""
app.py — Cyclone Disaster Prediction Dashboard
────────────────────────────────────────────────
A Streamlit-powered dashboard that combines ML predictions with
real-time API data to provide cyclone risk assessment for Indian
coastal cities.

Features:
  - City search with geocoding
  - Interactive Folium map with cyclone tracks & shelters
  - ML-powered prediction cards (rainfall, wind, risk)
  - Time-series charts for weather trends
  - Evacuation shelter locations

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Local modules
from api_client import (
    fetch_weather_forecast,
    fetch_weather_history,
    fetch_shelters_osm,
    get_default_shelters,
    get_simulated_active_cyclone,
    geocode_city,
    haversine_distance,
)
from prediction_pipeline import (
    load_models,
    run_full_prediction,
)

# ──────────────────── PAGE CONFIG ───────────────────────────────
st.set_page_config(
    page_title="CycloneGuard - Disaster Prediction Dashboard",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────── CUSTOM CSS ────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --bg-main: #f8fafc;
        --card-bg: #ffffff;
        --text-main: #0f172a;
        --text-sub: #475569;
        --border: #e2e8f0;
        
        /* Vibrant Status Colors */
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
    }

    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-main);
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.08) 0px, transparent 50%);
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-main) !important;
        letter-spacing: -0.02em;
    }

    /* Vibrant Header */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        padding: 4rem 2rem;
        border-radius: 30px;
        margin-bottom: 2.5rem;
        color: white;
        box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.4);
        text-align: center;
        position: relative;
        overflow: hidden;
        border: none;
    }
    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        color: white !important;
        text-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .main-header p {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin: 1rem 0 0;
        font-weight: 500;
    }

    /* Glowing Metric cards */
    .metric-card {
        background: white;
        border-radius: 24px;
        padding: 2.2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.15);
        border-color: var(--primary);
    }
    .metric-card .metric-label {
        font-size: 0.85rem;
        color: var(--text-sub);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.8rem;
    }
    .metric-card .metric-value {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        line-height: 1;
        margin: 0.5rem 0;
    }
    .metric-card .metric-sub {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 1rem;
        font-weight: 500;
    }

    /* Vibrant Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-main);
        margin: 3.5rem 0 1.5rem;
        padding-left: 1.2rem;
        border-left: 8px solid var(--accent);
        background: linear-gradient(90deg, #f1f5f9, transparent);
        border-radius: 0 10px 10px 0;
    }

    /* City Info container */
    .city-info-container {
        background: white;
        padding: 1.5rem 2.5rem;
        border-radius: 24px;
        box-shadow: 0 10px 20px -5px rgba(0,0,0,0.05);
        border-left: 8px solid var(--primary);
        margin-bottom: 2.5rem;
    }
    .city-info-text {
        font-size: 2.2rem; 
        font-weight: 800; 
        color: var(--text-main);
    }

    /* Vibrant Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        padding: 0.8rem;
        background: #f1f5f9;
        border-radius: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.8rem 1.8rem;
        border-radius: 14px !important;
        border: none !important;
        background: transparent !important;
        color: var(--text-sub) !important;
        font-weight: 700 !important;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2);
        transform: scale(1.05);
    }

    /* Risk Bar Glow */
    .risk-bar {
        background: #f1f5f9;
        border-radius: 20px;
        height: 12px;
        margin-top: 1.5rem;
        overflow: hidden;
    }
    .risk-fill-severe { background: var(--danger); box-shadow: 0 0 15px var(--danger); width: 95%; height: 100%; border-radius: 20px; }
    .risk-fill-high { background: #f97316; box-shadow: 0 0 15px #f97316; width: 75%; height: 100%; border-radius: 20px; }
    .risk-fill-medium { background: var(--warning); box-shadow: 0 0 15px var(--warning); width: 50%; height: 100%; border-radius: 20px; }
    .risk-fill-low { background: var(--success); box-shadow: 0 0 15px var(--success); width: 25%; height: 100%; border-radius: 20px; }

    /* Hide streamlit stuff */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Vibrant Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid var(--border);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-main); }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ──────────────────── LOAD DATA & MODELS ────────────────────────
@st.cache_resource
def get_models():
    try:
        return load_models()
    except Exception as e:
        return {"load_errors": [str(e)]}

models = get_models()
if "load_errors" in models:
    st.error("⚠️ Some AI models failed to load. Predictions may be unavailable.")
    with st.expander("Show Technical Details"):
        for err in models["load_errors"]:
            st.write(f"- {err}")


@st.cache_data(ttl=600)
def get_cached_weather(lat, lon):
    return fetch_weather_forecast(lat, lon, days=7), fetch_weather_history(lat, lon, days_back=14)


@st.cache_data(ttl=3600)
def get_cached_simulation(lat, lon):
    return get_simulated_active_cyclone(lat, lon)


@st.cache_data
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


# ──────────────────── HEADER ────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>Cyclone<span>Guard</span></h1>
    <p>Predictive safety dashboard for coastal communities</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Configuration")

    cities_df = get_city_database()
    city_list = cities_df["city"].tolist()

    city_option = st.selectbox(
        "Select a city",
        ["-- Select --"] + city_list + ["Custom City..."],
        index=0,
    )

    custom_city = None
    if city_option == "Custom City...":
        custom_city = st.text_input("Enter city name:", placeholder="e.g., Dhaka, Yangon")

    st.markdown("---")
    st.markdown("### 🌊 Cyclone Simulation")
    enable_cyclone_sim = st.toggle("Enable Cyclone Scenario", value=True)

    if enable_cyclone_sim:
        st.info("A simulated cyclone will be generated for demonstration. In production, this uses live IMD/NOAA feeds.")

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown("""
    <div class="info-box">
        <b>Weather:</b> Open-Meteo API (Live)<br>
        <b>Cyclone:</b> NOAA IBTrACS + IMD<br>
        <b>Shelters:</b> OSM Overpass API<br>
        <b>Analytics:</b> Historical Data Models
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Model Performance")
    models = get_models()
    if "rainfall_meta" in models:
        rm = models["rainfall_meta"]
        st.metric("Rainfall Model R²", f"{rm.get('r2', 0):.3f}")
    if "wind_meta" in models:
        wm = models["wind_meta"]
        st.metric("Wind Model R²", f"{wm.get('r2', 0):.3f}")


# ──────────────────── MAIN CONTENT ──────────────────────────────
selected_city = None
city_lat = None
city_lon = None
pop_density = 10000

if city_option == "Custom City..." and custom_city:
    geo = geocode_city(custom_city)
    if geo:
        selected_city = geo["name"]
        city_lat = geo["lat"]
        city_lon = geo["lon"]
        st.sidebar.success(f"Found: {geo['name']}, {geo.get('admin1', '')}, {geo.get('country', '')}")
    else:
        st.error(f"Could not find coordinates for '{custom_city}'. Please try another city name.")
elif city_option not in ["-- Select --", "Custom City..."]:
    selected_city = city_option
    row = cities_df[cities_df["city"] == city_option].iloc[0]
    city_lat = row["latitude"]
    city_lon = row["longitude"]
    pop_density = row.get("population_density", 10000)


if selected_city is None:
    # Landing page
    st.markdown("""
    <div style="text-align: center; padding: 6rem 1rem; background: rgba(255,255,255,0.4); border-radius: 40px; border: 1px solid rgba(255,255,255,0.7); backdrop-filter: blur(20px);">
        <h1 style="color: #0f172a; font-size: 3.5rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 1.5rem;">
            Secure Coastal <span>Intelligence</span>
        </h1>
        <p style="color: #64748b; font-size: 1.3rem; max-width: 700px; margin: 0 auto 2.5rem; line-height: 1.6;">
            Empowering decision-makers with real-time AI modeling, satellite telemetry, and hyper-local risk assessment. Secure your community against the elements.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px;">
             <span class="status-badge badge-live">Live Satellite Feed</span>
             <span class="status-badge" style="background:#dee2e6; color:#495057;">IMD Verified</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show test cities
    st.markdown('<div class="section-header">Recommended Cities</div>', unsafe_allow_html=True)

    test_cities = cities_df.head(10)
    cols = st.columns(5)
    for i, (_, row) in enumerate(test_cities.iterrows()):
        with cols[i % 5]:
            st.markdown(f"""
            <div class="metric-card" style="min-height: 100px; text-align: center;">
                <div class="metric-label">{row.get('population_density', 'N/A')} /km²</div>
                <div class="metric-value" style="font-size: 1.2rem;">{row['city']}</div>
                <div class="metric-sub">{row['latitude']:.2f}°N, {row['longitude']:.2f}°E</div>
            </div>
            """, unsafe_allow_html=True)

    st.stop()


# ──────────────────── FETCH LIVE DATA ───────────────────────────
with st.spinner("Fetching live weather data..."):
    weather_data, weather_history = get_cached_weather(city_lat, city_lon)

cyclone_data = None
if enable_cyclone_sim:
    with st.spinner("Gathering cyclone scenario data..."):
        cyclone_data = get_cached_simulation(city_lat, city_lon)

# ──────────────────── RUN PREDICTIONS ───────────────────────────
with st.spinner("Analyzing data and running analytics..."):
    models = get_models()
    predictions = run_full_prediction(
        city_name=selected_city,
        city_lat=city_lat,
        city_lon=city_lon,
        weather_data=weather_data,
        cyclone_data=cyclone_data if cyclone_data else {
            "wind_kmh": 0, "pressure_mb": 1013,
            "lat": city_lat, "lon": city_lon,
            "distance_km": 9999, "track": [],
        },
        population_density=pop_density,
        models=models,
    )

# ──────────────────── CITY INFO BAR ─────────────────────────────
current_weather = weather_data.get("current_weather", {}) if weather_data else {}
st.markdown('<div class="city-info-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2.5, 1, 1, 1])
with col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="width: 50px; height: 50px; background: #eff6ff; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 1.5rem;">📍</span>
        </div>
        <div>
            <div class="city-info-text">{selected_city}</div>
            <div style="color: #64748b; font-size: 0.9rem; font-weight: 500;">Coordinates: {city_lat:.4f}°N, {city_lon:.4f}°E</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.metric("Temperature", f"{current_weather.get('temperature', 'N/A')}°C")
with col3:
    st.metric("Wind Speed", f"{current_weather.get('windspeed', 'N/A')} km/h")
with col4:
    st.metric("Risk Forecast", "In Queue", "Live")
st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")


# ──────────────────── PREDICTION CARDS ──────────────────────────
st.markdown('<div class="section-header">Prediction Summary</div>', unsafe_allow_html=True)

# Calculate key metrics
avg_rainfall = 0
max_rainfall = 0
if predictions["rainfall"]["predictions"]:
    rainfalls = [p["predicted_rainfall_mm"] for p in predictions["rainfall"]["predictions"]]
    avg_rainfall = np.mean(rainfalls)
    max_rainfall = max(rainfalls)

forecast_avg_rainfall = 0
if weather_data and "daily" in weather_data:
    forecast_rain = [r or 0 for r in weather_data["daily"].get("rain_sum", [])]
    if forecast_rain:
        forecast_avg_rainfall = float(np.mean(forecast_rain))

rainfall_note = f"Max: {max_rainfall:.1f} mm | 7-day avg"
if avg_rainfall == 0 and forecast_avg_rainfall == 0:
    rainfall_note = "Dry forecast for next 7 days"

pred_wind = predictions["wind"]["predicted_wind_kmh"]
risk_level = predictions["risk"]["risk_level"]
risk_confidence = predictions["risk"]["confidence"]
cyclone_dist = cyclone_data["distance_km"] if cyclone_data else 9999
closest_approach = predictions["cyclone_path"].get("closest_approach_km", 9999)

# Risk color mapping
risk_colors = {
    "Severe": ("#ff0844", "risk-severe", "risk-fill-severe"),
    "High": ("#f5af19", "risk-high", "risk-fill-high"),
    "Medium": ("#f7971e", "risk-medium", "risk-fill-medium"),
    "Low": ("#11998e", "risk-low", "risk-fill-low"),
}
risk_color, risk_class, risk_fill = risk_colors.get(risk_level, ("#64748b", "risk-low", "risk-fill-low"))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 1rem;">🌧️</div>
        <div class="metric-label">Predicted Rainfall</div>
        <div class="metric-value" style="color: var(--primary);">{avg_rainfall:.1f} mm</div>
        <div class="metric-sub">{rainfall_note}</div>
        <div class="metric-sub">Forecast avg rain: {forecast_avg_rainfall:.1f} mm</div>
        <div class="metric-sub">Model R²: {predictions['rainfall'].get('model_r2', 0):.3f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 1rem;">💨</div>
        <div class="metric-label">Predicted Wind Speed</div>
        <div class="metric-value" style="color: #ea580c;">{pred_wind:.0f} km/h</div>
        <div class="metric-sub">{"Danger zone" if pred_wind > 100 else "Moderate winds" if pred_wind > 60 else "Safe conditions"} expected</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 1rem;">🌀</div>
        <div class="metric-label">Cyclone Distance</div>
        <div class="metric-value" style="color: #8b5cf6;">{cyclone_dist:.0f} km</div>
        <div class="metric-sub">Closest point in 24h: {closest_approach:.0f} km</div>
        <div class="metric-sub" style="font-weight: 600; color: {'#dc2626' if closest_approach < cyclone_dist else '#16a34a'};">
            {"⚠️ Approaching" if closest_approach < cyclone_dist else "✓ Moving away"}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 1rem;">🛡️</div>
        <div class="metric-label">Disaster Risk Level</div>
        <div class="metric-value {risk_class}">{risk_level.upper()}</div>
        <div class="metric-sub">Confidence: {risk_confidence * 100:.1f}%</div>
        <div class="risk-bar"><div class="{risk_fill}"></div></div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")


# ──────────────────── MAP & CHARTS ──────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Interactive Map", "Weather Trends", "Cyclone Analysis", "Evacuation Shelters"])

with tab1:
    st.markdown('<div class="section-header">Interactive Disaster Map</div>', unsafe_allow_html=True)

    # Create Folium map
    m = folium.Map(
        location=[city_lat, city_lon],
        zoom_start=7,
        tiles="CartoDB dark_matter",
    )

    # City marker
    folium.Marker(
        location=[city_lat, city_lon],
        popup=f"<b>{selected_city}</b><br>Lat: {city_lat:.4f}<br>Lon: {city_lon:.4f}",
        tooltip=selected_city,
        icon=folium.Icon(color="blue", icon="home", prefix="fa"),
    ).add_to(m)

    if cyclone_data:
        # Cyclone current position
        folium.Marker(
            location=[cyclone_data["lat"], cyclone_data["lon"]],
            popup=f"""
                <b>{cyclone_data['name']}</b><br>
                Category: {cyclone_data['category']}<br>
                Wind: {cyclone_data['wind_kmh']} km/h<br>
                Pressure: {cyclone_data['pressure_mb']} mb<br>
                Distance: {cyclone_data['distance_km']:.0f} km
            """,
            tooltip=cyclone_data["name"],
            icon=folium.Icon(color="red", icon="warning", prefix="fa"),
        ).add_to(m)

        # Cyclone danger radius
        folium.Circle(
            location=[cyclone_data["lat"], cyclone_data["lon"]],
            radius=150000,  # 150km
            color="#ff4444",
            fill=True,
            fill_opacity=0.15,
            weight=2,
            popup="Danger Zone (150km)",
        ).add_to(m)

        folium.Circle(
            location=[cyclone_data["lat"], cyclone_data["lon"]],
            radius=300000,  # 300km
            color="#ff8844",
            fill=True,
            fill_opacity=0.08,
            weight=1,
            dash_array="10",
            popup="Watch Zone (300km)",
        ).add_to(m)

        # Past track (solid line)
        track_coords = [(p["lat"], p["lon"]) for p in cyclone_data.get("track", [])]
        if track_coords:
            folium.PolyLine(
                track_coords,
                color="#ff6b6b",
                weight=3,
                opacity=0.8,
                tooltip="Past Track",
            ).add_to(m)

            # Track points
            for pt in cyclone_data.get("track", []):
                folium.CircleMarker(
                    location=[pt["lat"], pt["lon"]],
                    radius=4,
                    color="#ff6b6b",
                    fill=True,
                    fill_color="#ff6b6b",
                    fill_opacity=0.7,
                ).add_to(m)

        # Predicted track (dashed line)
        pred_coords = [(p["lat"], p["lon"]) for p in cyclone_data.get("predicted_track", [])]
        if not pred_coords and predictions["cyclone_path"]["predicted_positions"]:
            pred_coords = [
                (p["lat"], p["lon"])
                for p in predictions["cyclone_path"]["predicted_positions"]
            ]

        if pred_coords:
            # Add current position to start of predicted track
            pred_coords = [(cyclone_data["lat"], cyclone_data["lon"])] + pred_coords
            folium.PolyLine(
                pred_coords,
                color="#fbbf24",
                weight=3,
                opacity=0.7,
                dash_array="10 5",
                tooltip="Predicted Path (24h)",
            ).add_to(m)

            for pt in pred_coords[1:]:
                folium.CircleMarker(
                    location=pt,
                    radius=3,
                    color="#fbbf24",
                    fill=True,
                    fill_color="#fbbf24",
                    fill_opacity=0.6,
                ).add_to(m)

        # Distance line
        folium.PolyLine(
            [(city_lat, city_lon), (cyclone_data["lat"], cyclone_data["lon"])],
            color="#a78bfa",
            weight=2,
            opacity=0.5,
            dash_array="5 5",
            tooltip=f"Distance: {cyclone_data['distance_km']:.0f} km",
        ).add_to(m)

    # Rainfall heatmap (from forecast)
    if weather_data and "daily" in weather_data:
        rain_vals = weather_data["daily"].get("rain_sum", [])
        if any(r and r > 0 for r in rain_vals):
            # Generate heat points around city
            heat_data = []
            for r in rain_vals:
                if r and r > 0:
                    for _ in range(int(min(r, 50))):
                        h_lat = city_lat + np.random.uniform(-0.3, 0.3)
                        h_lon = city_lon + np.random.uniform(-0.3, 0.3)
                        heat_data.append([h_lat, h_lon, r])
            if heat_data:
                HeatMap(
                    heat_data,
                    name="Rainfall Intensity",
                    radius=25,
                    blur=15,
                    gradient={0.2: "blue", 0.4: "cyan", 0.6: "lime", 0.8: "yellow", 1: "red"},
                ).add_to(m)

    # Add shelters
    shelters = fetch_shelters_osm(city_lat, city_lon, radius_km=20)
    if not shelters:
        shelters = get_default_shelters(selected_city)

    shelter_group = folium.FeatureGroup(name="Evacuation Shelters")
    for s in shelters:
        if s["lat"] and s["lon"]:
            folium.Marker(
                location=[s["lat"], s["lon"]],
                popup=f"<b>{s['name']}</b><br>Type: {s.get('type', 'shelter')}",
                tooltip=s["name"],
                icon=folium.Icon(color="green", icon="plus-square", prefix="fa"),
            ).add_to(shelter_group)
    shelter_group.add_to(m)

    folium.LayerControl().add_to(m)

    # Legend
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 999;
        background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.1); color: #0f172a; font-size: 13px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <b>Legend</b><br>
        🔴 Cyclone Position<br>
        <span style="color:#ff6b6b;">━━</span> Past Track<br>
        <span style="color:#fbbf24;">╌╌</span> Predicted Path<br>
        🟢 Evacuation Shelter<br>
        🔵 City Location<br>
        🟣 Distance Line
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=550, returned_objects=[])


with tab2:
    st.markdown('<div class="section-header">Weather Forecast & Predictions</div>', unsafe_allow_html=True)

    if weather_data and "daily" in weather_data:
        daily = weather_data["daily"]
        dates = daily.get("time", [])

        # Rainfall chart
        col1, col2 = st.columns(2)

        with col1:
            fig_rain = go.Figure()

            actual_rain = [r or 0 for r in daily.get("rain_sum", [])]
            pred_rain = [p["predicted_rainfall_mm"] for p in predictions["rainfall"]["predictions"]]

            fig_rain.add_trace(go.Bar(
                x=dates, y=actual_rain,
                name="Forecast Rain (Open-Meteo)",
                marker_color="rgba(96, 165, 250, 0.7)",
            ))

            if pred_rain:
                fig_rain.add_trace(go.Scatter(
                    x=dates[:len(pred_rain)], y=pred_rain,
                    name="Predicted Rain",
                    mode="lines+markers",
                    line=dict(color="#f59e0b", width=3),
                    marker=dict(size=8),
                ))

            fig_rain.update_layout(
                title="Rainfall Forecast vs Predicted Rainfall",
                xaxis_title="Date",
                yaxis_title="Rainfall (mm)",
                template="plotly_white",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_rain, use_container_width=True)

        with col2:
            fig_wind = go.Figure()

            wind_max = [w or 0 for w in daily.get("windspeed_10m_max", [])]
            wind_gust = [w or 0 for w in daily.get("windgusts_10m_max", [])]

            fig_wind.add_trace(go.Scatter(
                x=dates, y=wind_max,
                name="Max Wind Speed",
                mode="lines+markers",
                line=dict(color="#60a5fa", width=2),
                fill="tozeroy",
                fillcolor="rgba(96, 165, 250, 0.1)",
            ))
            fig_wind.add_trace(go.Scatter(
                x=dates, y=wind_gust,
                name="Wind Gusts",
                mode="lines+markers",
                line=dict(color="#f87171", width=2, dash="dot"),
            ))

            # Add danger threshold
            fig_wind.add_hline(
                y=62, line_dash="dash", line_color="red",
                annotation_text="Storm threshold (62 km/h)",
            )

            fig_wind.update_layout(
                title="Wind Speed Trend",
                xaxis_title="Date",
                yaxis_title="Speed (km/h)",
                template="plotly_white",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_wind, use_container_width=True)

        # Temperature chart
        fig_temp = go.Figure()
        temp_max = [t or 0 for t in daily.get("temperature_2m_max", [])]
        temp_min = [t or 0 for t in daily.get("temperature_2m_min", [])]

        fig_temp.add_trace(go.Scatter(
            x=dates, y=temp_max,
            name="Max Temp",
            mode="lines",
            line=dict(color="#ef4444", width=2),
        ))
        fig_temp.add_trace(go.Scatter(
            x=dates, y=temp_min,
            name="Min Temp",
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(239, 68, 68, 0.1)",
            line=dict(color="#3b82f6", width=2),
        ))

        fig_temp.update_layout(
            title="Temperature Range",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            template="plotly_white",
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    else:
        st.warning("Weather data unavailable. Check your internet connection.")


with tab3:
    st.markdown('<div class="section-header">Cyclone Analysis & Path Prediction</div>', unsafe_allow_html=True)

    if cyclone_data:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #dc2626; margin-top: 0; font-weight: 800;">{cyclone_data['name']}</h3>
                <table style="width: 100%; color: #0f172a; border-collapse: separate; border-spacing: 0 8px;">
                    <tr><td style="color: #64748b; font-weight: 500;">Category</td><td><b style="color: #0f172a;">{cyclone_data['category']}</b></td></tr>
                    <tr><td style="color: #64748b; font-weight: 500;">Basin</td><td><b>{cyclone_data['basin']}</b></td></tr>
                    <tr><td style="color: #64748b; font-weight: 500;">Position</td><td><b>{cyclone_data['lat']}°N, {cyclone_data['lon']}°E</b></td></tr>
                    <tr><td style="color: #64748b; font-weight: 500;">Wind Speed</td><td><b style="color: #ea580c;">{cyclone_data['wind_kmh']} km/h</b></td></tr>
                    <tr><td style="color: #64748b; font-weight: 500;">Pressure</td><td><b>{cyclone_data['pressure_mb']} mb</b></td></tr>
                    <tr><td style="color: #64748b; font-weight: 500;">Distance to {selected_city}</td><td><b style="color: #2563eb;">{cyclone_data['distance_km']:.0f} km</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Cyclone distance time series
            if predictions["cyclone_path"]["predicted_distances"]:
                distances = predictions["cyclone_path"]["predicted_distances"]
                hours = [i * 3 for i in range(1, len(distances) + 1)]

                fig_dist = go.Figure()
                fig_dist.add_trace(go.Scatter(
                    x=hours, y=distances,
                    mode="lines+markers",
                    name="Predicted Distance",
                    line=dict(color="#a78bfa", width=3),
                    marker=dict(size=8),
                    fill="tozeroy",
                    fillcolor="rgba(167, 139, 250, 0.1)",
                ))

                # Danger thresholds
                fig_dist.add_hline(y=200, line_dash="dash", line_color="red",
                                   annotation_text="High Risk (<200 km)")
                fig_dist.add_hline(y=500, line_dash="dash", line_color="orange",
                                   annotation_text="Watch Zone (<500 km)")

                fig_dist.update_layout(
                    title=f"Cyclone Distance from {selected_city}",
                    xaxis_title="Hours Ahead",
                    yaxis_title="Distance (km)",
                    template="plotly_white",
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_dist, use_container_width=True)

        # Cyclone track intensity
        if cyclone_data.get("track"):
            st.markdown("#### Storm Intensity Along Track")
            track = cyclone_data["track"]
            track_df = pd.DataFrame(track)

            fig_intensity = go.Figure()
            fig_intensity.add_trace(go.Scatter(
                x=list(range(len(track_df))),
                y=track_df["wind_kmh"],
                name="Wind Speed",
                mode="lines+markers",
                line=dict(color="#ef4444", width=2),
                yaxis="y1",
            ))
            fig_intensity.add_trace(go.Scatter(
                x=list(range(len(track_df))),
                y=track_df["pressure_mb"],
                name="Pressure",
                mode="lines+markers",
                line=dict(color="#3b82f6", width=2),
                yaxis="y2",
            ))

            fig_intensity.update_layout(
                title="Storm Intensity (Wind & Pressure)",
                template="plotly_dark",
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="Wind Speed (km/h)", side="left", color="#ef4444"),
                yaxis2=dict(title="Pressure (mb)", side="right", overlaying="y", color="#3b82f6"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_intensity, use_container_width=True)

        # Risk probabilities
        if "probabilities" in predictions["risk"]:
            st.markdown("#### Risk Level Probabilities")
            probs = predictions["risk"]["probabilities"]
            prob_df = pd.DataFrame({
                "Risk Level": list(probs.keys()),
                "Probability": list(probs.values()),
            })

            risk_order_colors = {
                "Low": "#38ef7d", "Medium": "#ffd200",
                "High": "#f5af19", "Severe": "#ff0844",
            }
            fig_risk = go.Figure()
            for _, row in prob_df.iterrows():
                fig_risk.add_trace(go.Bar(
                    x=[row["Risk Level"]],
                    y=[row["Probability"]],
                    name=row["Risk Level"],
                    marker_color=risk_order_colors.get(row["Risk Level"], "#64748b"),
                ))
            fig_risk.update_layout(
                title="Risk Level Classification Probabilities",
                yaxis_title="Probability",
                template="plotly_dark",
                height=350,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig_risk, use_container_width=True)
    else:
        st.info("Enable Cyclone Simulation in the sidebar to see cyclone analysis.")


with tab4:
    st.markdown('<div class="section-header">Evacuation Shelters & Emergency Resources</div>', unsafe_allow_html=True)

    with st.spinner("Searching for nearby shelters..."):
        shelters = fetch_shelters_osm(city_lat, city_lon, radius_km=20)
        if not shelters:
            shelters = get_default_shelters(selected_city)

    if shelters:
        st.success(f"Found {len(shelters)} evacuation shelters near {selected_city}")

        # Shelter map
        shelter_map = folium.Map(
            location=[city_lat, city_lon],
            zoom_start=12,
            tiles="CartoDB positron",
        )
        folium.Marker(
            location=[city_lat, city_lon],
            popup=f"<b>{selected_city}</b>",
            icon=folium.Icon(color="blue", icon="home", prefix="fa"),
        ).add_to(shelter_map)

        for s in shelters:
            if s["lat"] and s["lon"]:
                dist = haversine_distance(city_lat, city_lon, s["lat"], s["lon"])
                folium.Marker(
                    location=[s["lat"], s["lon"]],
                    popup=f"<b>{s['name']}</b><br>Type: {s.get('type', 'shelter')}<br>Distance: {dist:.1f} km",
                    tooltip=s["name"],
                    icon=folium.Icon(color="green", icon="plus-square", prefix="fa"),
                ).add_to(shelter_map)

        st_folium(shelter_map, width=None, height=450, returned_objects=[])

        # Shelter list
        st.markdown("#### Shelter Details")
        shelter_data = []
        for s in shelters:
            if s["lat"] and s["lon"]:
                dist = haversine_distance(city_lat, city_lon, s["lat"], s["lon"])
                shelter_data.append({
                    "Name": s["name"],
                    "Type": s.get("type", "shelter"),
                    "Latitude": s["lat"],
                    "Longitude": s["lon"],
                    "Distance (km)": round(dist, 2),
                })
        if shelter_data:
            shelter_df = pd.DataFrame(shelter_data)
            shelter_df = shelter_df.sort_values("Distance (km)")
            st.dataframe(shelter_df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No shelters found near {selected_city}. Try expanding the search radius.")


# ──────────────────── FOOTER ────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p><b>CycloneGuard</b> — Cyclone Data Dashboard</p>
    <p>Data: Open-Meteo | NOAA | OpenStreetMap | IMD</p>
    <p style="font-size: 0.8rem;">For educational and research purposes. Always follow official government advisories.</p>
</div>
""", unsafe_allow_html=True)
