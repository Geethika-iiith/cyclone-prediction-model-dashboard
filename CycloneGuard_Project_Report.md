# Cyclone Guard: Comprehensive Project Report
## Team Aftershock: Predictive Cyclone Intelligence

**Team Members:**
- Geethika Palla
- Aniket Verma
- Koustubh Jain

---

## 1. Abstract
CycloneGuard is an AI-powered cyclone prediction and management ecosystem developed to mitigate the impact of tropical cyclones on coastal communities. By integrating real-time telemetry from global weather APIs (Open-Meteo, NOAA) and safe evacuation data from OpenStreetMap, the dashboard provides hyper-local risk indices. The core predictive engine utilizes XGBoost and Random Forest algorithms to forecast rainfall intensities and wind speeds with high precision, presented through a modern "Electric Indigo" glassmorphism interface.

## 2. Problem Statement
India's coastline, particularly the Bay of Bengal and Arabian Sea regions, is consistently threatened by intense cyclonic activities. Existing government bulletins are often technical and lack granular, city-specific predictive insights (e.g., "what will the rainfall be in Mumbai specifically?"). Furthermore, locating shelters during active storms is a significant challenge for displaced populations. CycloneGuard addresses these gaps with a unified, predictive, and user-centric platform.

## 3. System Components & Architecture
### 3.1 Data Ingestion Layer
- **Weather API**: Live forecast data for the next 7 days (Open-Meteo).
- **Cyclone Telemetry**: Active storm tracks and intensity logs (NOAA IBTrACS).
- **Shelter Geolocation**: Real-time OSM Overpass queries for safe zones within a 20km radius.

### 3.2 Machine Learning Pipeline
The pipeline is designed for robustness and low latency:
- **Rainfall Model**: An XGBoost Regressor trained on 20+ years of historical Indian weather data. It uses lag features (1d, 3d, 7d) and seasonal weights.
- **Wind Model**: A Random Forest Regressor predicting sustained wind speeds based on central pressure and latitude/longitude coordinates.
- **Risk Classifier**: A multi-class classifier that labels cities into **Low, Medium, High, or Severe** risk zones based on weather predictions and population density.

### 3.3 Frontend Dashboard
Built with Streamlit and styled with custom CSS:
- **Theme**: "Midnight Indigo" with vibrant glowing metrics.
- **Interactivity**: Dynamic filtering of coastal cities, interactive Folium maps, and real-time chart rendering.

## 4. Key Results & Achievements
- **Predictive Accuracy**: Achieved an R2 score of 0.85 on wind speed forecasting during validation.
- **Consistency**: Implemented server-side caching (TTL 600s) to ensure consistent data delivery across multiple users.
- **Deployment**: Successfully hosted on Streamlit Community Cloud with cross-platform compatibility (Windows/Linux/Mobile).

## 5. Visual Evidence
### 5.1 Landing Page
The dashboard opens to a curated selection of high-risk coastal cities with real-time population density and risk status.

### 5.2 Mumbai Case Study
Predictive analytics for Mumbai showing exact rainfall forecasts in mm and sustained wind speeds, alongside an evacuation map.

## 6. Conclusion
Team Aftershock has developed CycloneGuard as a scalable solution for disaster resilience. The project successfully bridges the gap between complex climate science and accessible citizen-facing intelligence.

---
*Report Date: March 16, 2026*
*Software Version: 2.1.0-Indigo*
