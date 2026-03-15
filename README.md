# CycloneGuard: Predictive Disaster Intelligence

CycloneGuard is an AI-powered disaster prediction dashboard designed for coastal communities. It combines machine learning models with real-time satellite telemetry to provide hyper-local risk assessments, weather forecasts, and evacuation shelter mapping.

## 🌟 Key Features
- **AI-Powered Risk Assessment**: Real-time disaster risk level prediction (Severe, High, Medium, Low) based on historical and live data.
- **Predictive Analytics**: 7-day rainfall and wind speed forecasting using advanced ML models.
- **Interactive Disaster Map**: Visualizes predicted cyclone tracks, city buffers, and safe evacuation zones.
- **Live Data Integration**: Fetches real-time weather from Open-Meteo, cyclone data from NOAA/IMD, and shelter locations from OpenStreetMap.
- **Vibrant UI/UX**: Professional "Electric Indigo" dashboard featuring glassmorphism and modern typography.

## 🛠️ Technology Stack
- **Frontend**: Streamlit, HTML5, CSS3 (Glassmorphism)
- **Mapping**: Folium, Leaflet.js
- **Machine Learning**: Scikit-learn, XGBoost, Pandas, NumPy
- **APIs**: Open-Meteo, NOAA/IMD (via API Client), OpenStreetMap (Overpass API)
- **Deployment**: Streamlit Community Cloud

## 🚀 Installation & Local Run
1. Clone the repository:
   ```bash
   git clone https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard.git
   cd cyclone-prediction-model-dashboard
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python -m streamlit run app.py
   ```

## 📊 Project Structure
- `app.py`: Main dashboard logic and UI styling.
- `prediction_pipeline.py`: Core ML logic for rainfall, wind, and risk prediction.
- `api_client.py`: Data ingestion layer for weather, cyclone, and shelter APIs.
- `models/`: Pre-trained ML models for localized forecasting.

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.
