# Cyclone Guard: Predictive Cyclone Intelligence
### Team Aftershock: Geethika Palla | Aniket Verma | Koustubh Jain

CycloneGuard is an AI-powered cyclone prediction dashboard designed for coastal communities. It combines machine learning models with real-time satellite telemetry to provide hyper-local risk assessments, weather forecasts, and evacuation shelter mapping.

## ✨ Project Highlights
- **🌟 AI-Powered Risk Assessment**: Real-time cyclone risk level prediction (Severe, High, Medium, Low) using weighted ML variables.
- **📈 Predictive Analytics**: 7-day rainfall and wind speed forecasting powered by **XGBoost** and **Random Forest**.
- **🗺️ Interactive Cyclone Map**: Visualizes predicted cyclone tracks, city safety buffers, and nearest safe shelters.
- **🛰️ Live Data Integration**: Zero-latency fetching from Open-Meteo, NOAA/IBTrACS, and OpenStreetMap.
- **💎 Vibrant UI/UX**: Professional "Midnight Indigo" theme featuring glassmorphism and motion design.

## 🛠️ Technology Stack
- **Dashboard**: Streamlit (Python)
- **ML Engine**: Scikit-Learn, XGBoost
- **Geodata**: Folium, Leaflet, Geodesic distance modeling
- **Backend APIs**: Open-Meteo, NOAA, OSM Overpass
- **Deployment**: Streamlit Cloud

## 🚀 Quick Start
1. Clone the repo: `git clone https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard.git`
2. Install: `pip install -r requirements.txt`
3. Launch: `python -m streamlit run app.py`

## 📊 Documentation
- [View Full Project Report](./CycloneGuard_Project_Report.md)
- [Download Presentation](./CycloneGuard_Project_Presentation.pptx)

## 🛡️ License
Distributed under the MIT License. Developed by **Team Aftershock**.
