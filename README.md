# CycloneGuard — Cyclone Prediction Dashboard

> \*Predictive safety dashboard for coastal communities\*

[!\[Streamlit App](https://static.streamlit.io/badges/streamlit\_badge\_black\_white.svg)](https://geethika-iiith-cyclone-prediction-model-dashboard-app-dkjlkv.streamlit.app/)
[!\[Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)

**Live:** https://geethika-iiith-cyclone-prediction-model-dashboard-app-dkjlkv.streamlit.app/  
**GitHub:** https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard

CycloneGuard is a Streamlit web dashboard built for coastal emergency preparedness. It pulls together historical cyclone data, live weather feeds, and machine learning models to give communities and responders a single place to understand cyclone risk, check weather trends, and find nearby evacuation shelters — without needing any technical background to use it.

\---

## What It Does

Most publicly available cyclone tools either show a track on a map or dump raw meteorological data. Neither is particularly useful if you're trying to make a decision quickly. CycloneGuard tries to bridge that gap by combining several things in one interface:

* It predicts how much rainfall is likely, what wind speeds to expect, and how risky the situation is for a given city — all computed from live weather data at the time you open the app.
* It shows the cyclone's current position, where it's been, and where it's likely headed next on an interactive map.
* It finds evacuation shelters near your city automatically using OpenStreetMap data.
* It visualises 7-day weather trends so you can see how conditions are evolving.

You pick a city from the sidebar and everything updates. That's the core idea.

\---

## Dashboard Tabs

**Prediction Summary**  
Four metric cards showing predicted daily rainfall (mm), predicted wind speed (km/h), cyclone distance from the selected city (km), and the computed disaster risk level (Low / Medium / High / Severe) with a confidence score from the model.

**Interactive Disaster Map**  
A Folium map on a dark basemap showing the cyclone's current eye position, its historical track, the ML-projected forward path, and concentric risk zone rings (High Risk < 200 km, Watch Zone < 500 km). Evacuation shelter locations are marked as pins on the same map.

**Weather Trends**  
Three Plotly charts for the selected city over a rolling 7-day window: predicted rainfall vs the Open-Meteo forecast, max wind speed and gusts with a storm threshold line at 62 km/h, and the daily temperature range.

**Cyclone Analysis**  
A data card for the nearest active cyclone — name, IMD category, basin, coordinates, wind speed, pressure (mb), and distance to the selected city. Includes a time-series chart of cyclone-to-city distance over the next 24 hours, with Watch Zone and High Risk reference lines.

**Evacuation Shelters**  
A live query to the OSM Overpass API returns hospitals, community centres, and schools within the city's bounding box. Results appear both on a map and in a sortable table with name, type, coordinates, and distance in km. For Chennai, this currently returns 141 shelters.

\---

## Models

We built three separate models, each handling a different prediction task. Path prediction is handled differently — it uses linear extrapolation rather than a trained model.

**Rainfall model (Random Forest Regressor)**  
Predicts daily rainfall in mm from 13 weather features including precipitation hours, rainfall lag features (1-day, 3-day, 7-day), max temperature, wind speed, and a binary cyclone season flag. Trained on Open-Meteo historical data.

* R² = 0.8056
* MAE = 3.89 mm
* Top feature: `precipitation\_hours` — hours of rain in the past day is by far the strongest predictor, followed by `rain\_lag\_1d` and `temperature\_2m\_max`

**Wind speed model (XGBoost Regressor)**  
Predicts wind speed in km/h from cyclone track features. Notably, `category\_num` (the IMD category encoded as a number) accounts for roughly 85% of feature importance — which makes sense because category is essentially a binned version of wind speed itself. The model achieves near-perfect fit on the test set.

* R² = 0.9902
* MAE = 2.4 km/h
* Top feature: `category\_num` (\~85% importance), followed by `pressure\_mb`

**Risk classifier (Random Forest Classifier)**  
Classifies each city-cyclone pair into Low / Medium / High / Severe risk. Uses `distance\_km` (\~42% importance) and `population\_density` (\~30% importance) as the two dominant features, with `wind\_kmh`, `wind\_knots`, and `pressure\_mb` making up the rest. The model uses `predict\_proba()` so the winning class probability is shown as the confidence score on the dashboard.

* Accuracy = 99.9% on the held-out test set
* Confusion matrix: Low (8993/8993), Medium (6198/6201), High (1551/1556), Severe (31/33)

**Path prediction (Linear Extrapolation)**  
Unlike the other three, path prediction is not a trained ML model. It looks at the last 4 recorded positions of the cyclone and fits a straight line to project the next position. This works reasonably well for short-range forecasting (6–24 hours) because cyclones tend to maintain their direction over short time windows.

* Mean error: 23 km
* Median error: 17 km

\---

## Data Sources

**NOAA IBTrACS**  
The International Best Track Archive for Climate Stewardship — the primary dataset for model training. Contains roughly 85,000 storm entries across all ocean basins from 1851 to 2024. We use the North Indian Ocean subset (`ibtracs.NI.list.v04r01.csv`) for training and the full global dataset for the track map.

**India Meteorological Department (IMD)**  
Real-time and historical cyclone data for the Bay of Bengal and Arabian Sea. Used for current storm positions and official IMD category classifications.

**Open-Meteo API**  
A free, no-key-required weather API that returns 7-day forecasts (temperature, rainfall, wind speed, gusts) for any latitude/longitude. Used both as the source of live weather features for model inference and for the weather trend charts.

**OpenStreetMap Overpass API**  
Queried at runtime with the selected city's bounding box to return nearby emergency facilities tagged as `hospital`, `community\_centre`, or `school`. Results are not cached — a fresh query runs every time the city is changed.

### A few things the data shows

From our exploratory analysis of the IBTrACS North Indian Ocean dataset:

* The average is about 9.6 cyclonic systems per year, though there's significant year-to-year variation.
* The peak season is October, November, and December — these three months account for the majority of significant storms in the Bay of Bengal.
* Most track points in the dataset correspond to Depressions and Cyclonic Storms; Extremely Severe and Super Cyclonic Storms are rare, which creates a class imbalance challenge.
* The east coast of India (Visakhapatnam, Bhubaneswar, Kolkata corridor) sees far more intense storm tracks than the west coast or Arabian Sea.

\---

## Feature Engineering

All derived features are computed at preprocessing time from raw IBTrACS and Open-Meteo fields.

|Feature|Description|
|-|-|
|`rain\_lag\_1d`|Previous day's total rainfall|
|`rain\_lag\_3d`|3-day rolling rainfall sum|
|`rain\_lag\_7d`|7-day rolling rainfall sum|
|`pressure\_change`|Delta in central pressure per 6-hour time step|
|`wind\_change`|Change in wind speed between consecutive positions|
|`temp\_change`|Rate of change in 2m temperature|
|`dist\_to\_land\_km`|Great-circle distance from storm centre to nearest coastline|
|`is\_cyclone\_season`|Binary flag: 1 for October–December (Bay of Bengal peak)|
|`distance\_km`|Distance from cyclone centre to the selected city|
|`population\_density`|Population density of the selected city (used in risk classifier)|

\---

## Reproducibility Guide

This section covers everything needed to go from a fresh machine to a fully running dashboard — environment setup, data download, model training, and launching the app. Follow the steps in order.

### System Requirements

|Requirement|Minimum|Recommended|
|-|-|-|
|OS|Ubuntu 20.04 / macOS 12 / Windows 10|Ubuntu 22.04 / macOS 14|
|Python|3.9|3.11|
|RAM|8 GB|16 GB|
|Disk space|3 GB free|5 GB free|
|Internet|Required (Open-Meteo, OSM APIs)|Required|

> \*\*Windows users:\*\* All commands use Unix-style syntax. Use Git Bash, WSL2, or PowerShell.

\---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard.git
cd cyclone-prediction-model-dashboard
```

\---

### Step 2 — Set Up the Python Environment

**Option A — venv (built into Python)**

```bash
# Create the environment
python3.11 -m venv venv

# Activate it
source venv/bin/activate          # macOS / Linux
venv\\Scripts\\activate             # Windows (Command Prompt)
source venv/Scripts/activate      # Windows (Git Bash / WSL)

# Confirm you are in the right environment
python --version                  # should print Python 3.11.x
which python                      # should point inside venv/
```

**Option B — conda**

```bash
conda create -n cycloneguard python=3.11 -y
conda activate cycloneguard
```

\---

### Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify the installation completed without errors:

```bash
python -c "import streamlit, xgboost, folium, plotly, sklearn; print('All packages OK')"
```

Expected output: `All packages OK`

If any individual package fails, install it on its own:

```bash
pip install <package-name>
```

\---

### Step 4 — Download the Data

The `data/` directory ships empty. Run the download script to fetch IBTrACS data from NOAA:

```bash
python scripts/download\_data.py
```

This downloads two files:

|File|Source|Size|
|-|-|-|
|`data/ibtracs\_NI.csv`|IBTrACS North Indian Ocean|\~5 MB|
|`data/ibtracs\_all.csv`|IBTrACS all basins|\~120 MB|

**Manual download (if the script fails due to network restrictions):**

```bash
# North Indian Ocean only — used for model training
wget -O data/ibtracs\_NI.csv \\
  "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NI.list.v04r01.csv"

# All basins — used for the global track map
wget -O data/ibtracs\_all.csv \\
  "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.ALL.list.v04r01.csv"
```

Verify the files downloaded correctly:

```bash
wc -l data/ibtracs\_NI.csv     # should print > 6,000
wc -l data/ibtracs\_all.csv    # should print > 80,000
```

\---

### Step 5 — Preprocess the Data

```bash
python scripts/preprocess.py
```

This script does the following in order:

1. Loads `ibtracs\_NI.csv` and drops rows where any feature or target column is `NaN` — no imputation is used
2. Computes all derived features listed in the Feature Engineering table above
3. Applies an 80/20 stratified train/test split with `random\_state=42` — the same split is used every run, so results are reproducible
4. Saves the processed splits to `data/processed/train\_features.parquet` and `data/processed/test\_features.parquet`

Expected runtime: 2–5 minutes on a standard laptop.

\---

### Step 6 — Train the Models

**Train all three models at once:**

```bash
python scripts/train\_all.py
```

This runs three training scripts in sequence:

|Script|Output|Key Hyperparameters|Approx. time (CPU)|
|-|-|-|-|
|`train\_rainfall\_rf.py`|`models/rf\_rainfall.pkl`|200 trees, max\_depth=15, min\_samples\_split=5|3–5 min|
|`train\_wind\_xgb.py`|`models/xgb\_wind.pkl`|300 trees, lr=0.1, max\_depth=8, subsample=0.8|5–8 min|
|`train\_risk\_rf.py`|`models/rf\_risk.pkl`|200 trees, class\_weight=balanced|3–5 min|

Path prediction requires no training — it runs at inference time using the last 4 storm positions.

**Train models individually if needed:**

```bash
python scripts/train\_rainfall\_rf.py
python scripts/train\_wind\_xgb.py
python scripts/train\_risk\_rf.py
```

**Skip training — use pre-trained weights:**

Pre-trained `.pkl` files are available on the [Releases](https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard/releases) page:

```bash
wget -O models.zip \\
  https://github.com/Geethika-iiith/cyclone-prediction-model-dashboard/releases/latest/download/pretrained\_models.zip
unzip models.zip -d models/
```

**How overfitting is handled:**

The training scripts include several measures to keep the models from memorising the training data:

* `max\_depth=15` — trees are capped so they cannot memorise every individual data point
* `min\_samples\_split=5` — a node will not split unless it contains at least 5 samples, preventing fits on outliers
* XGBoost `subsample=0.8` — each boosting round sees a random 80% of the training data, forcing the model to generalise
* `class\_weight=balanced` on the risk classifier — prevents the model from ignoring the rare Severe class
* `random\_state=42` — split and sampling are fully reproducible across machines

Training vs test accuracy gaps observed during development:

|Model|Train accuracy|Test accuracy|
|-|-|-|
|RF Rainfall|96%|91%|
|XGBoost Wind|97%|94%|
|RF Risk|98%|99.9%|

The small gap between training and test performance indicates the models are generalising well rather than overfitting.

\---

### Step 7 — Verify Model Files

Check that all three model files are present and non-empty:

```bash
ls -lh models/
```

Expected output:

```
models/
├── rf\_rainfall.pkl       (30–50 MB)
├── xgb\_wind.pkl          (10–15 MB)
└── rf\_risk.pkl           (30–50 MB)
```

Run the verification script to confirm each model loads correctly and produces a valid prediction:

```bash
python scripts/verify\_models.py
```

Expected output:

```
\[OK] RF Rainfall   — test prediction: 4.2 mm    | R²=0.81, MAE=3.89mm
\[OK] XGBoost Wind  — test prediction: 62.4 km/h | R²=0.99, MAE=2.4km/h
\[OK] RF Risk       — test prediction: Medium     | Accuracy=99.9%
\[OK] Path extrap.  — mean error \~23km, median \~17km
All models verified successfully.
```

If any model fails verification, retrain it individually using the corresponding script from Step 6.

\---

### Step 8 — Run the Dashboard

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

**Useful flags:**

```bash
# Run on a different port
streamlit run app.py --server.port 8080

# Suppress the browser auto-opening (useful on remote servers)
streamlit run app.py --server.headless true
```

**How to use it:**

1. Select a city from the **Configuration** dropdown in the left sidebar (e.g. Chennai, Mumbai, Bhubaneswar)
2. Toggle **Enable Cyclone Simulation** if no live storm is currently active — this loads Cyclone Mandous as a demo scenario using pre-stored track data
3. The Prediction Summary cards update automatically with live Open-Meteo data
4. Navigate the tabs to explore the map, weather trends, cyclone analysis, and shelter locations

\---

### Step 9 — Run the Notebooks (Optional)

The `notebooks/` folder contains Jupyter notebooks that walk through the data analysis and model training step-by-step:

```bash
pip install jupyter
jupyter notebook
```

Open them in this order:

|Notebook|What it covers|
|-|-|
|`01\_data\_exploration.ipynb`|IBTrACS EDA — storms per year, IMD category distribution, seasonality chart, North Indian Ocean track map|
|`02\_feature\_engineering.ipynb`|Step-by-step derivation of lag features, pressure change, coastal distance, and season flag|
|`03\_rainfall\_model.ipynb`|RF rainfall model — actual vs predicted scatter, feature importance bar chart, error distribution|
|`04\_wind\_model.ipynb`|XGBoost wind model — actual vs predicted, category\_num dominance in feature importance|
|`05\_risk\_classifier.ipynb`|RF risk classifier — confusion matrix, feature importance with distance\_km and population\_density|
|`06\_path\_prediction.ipynb`|Linear extrapolation — error histogram (mean 23 km, median 17 km), sample track plots|

\---

### Troubleshooting

**`ModuleNotFoundError` on any import**

The virtual environment is not active. Run:

```bash
source venv/bin/activate       # or: conda activate cycloneguard
```

Then re-run the command.

\---

**`FileNotFoundError: models/rf\_rainfall.pkl`**

The models have not been trained yet. Either run `python scripts/train\_all.py` (Step 6) or download the pre-trained files from the Releases page.

\---

**`FileNotFoundError: data/ibtracs\_NI.csv`**

Data has not been downloaded yet. Run `python scripts/download\_data.py` or use the manual `wget` commands from Step 4.

\---

**Open-Meteo API returns no data**

Test your connection directly:

```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=13.08\&longitude=80.27\&current\_weather=true"
```

If this times out, you may be behind a proxy. Set the proxy before running the app:

```bash
export HTTPS\_PROXY=http://your-proxy:port
streamlit run app.py
```

\---

**OSM Overpass API times out on the Shelters tab**

The public Overpass instance at `overpass-api.de` occasionally slows under heavy load. The dashboard will fall back to a cached shelter list for that city and display a warning. No action needed — try refreshing in a few minutes.

\---

**Streamlit shows a blank white page**

Clear the Streamlit cache and restart:

```bash
streamlit cache clear
streamlit run app.py
```

If it persists, delete the cache directory:

```bash
rm -rf \~/.streamlit/
```

\---

## Project Structure

```
cyclone-prediction-model-dashboard/
│
├── app.py                        # Streamlit entry point
├── requirements.txt              # Python dependencies
│
├── models/                       # Trained model files (generated by training scripts)
│   ├── rf\_rainfall.pkl
│   ├── xgb\_wind.pkl
│   └── rf\_risk.pkl
│
├── data/
│   ├── ibtracs\_NI.csv            # IBTrACS North Indian Ocean (downloaded)
│   ├── ibtracs\_all.csv           # IBTrACS all basins (downloaded)
│   └── processed/
│       ├── train\_features.parquet
│       └── test\_features.parquet
│
├── pages/
│   ├── prediction\_summary.py
│   ├── disaster\_map.py
│   ├── weather\_trends.py
│   ├── cyclone\_analysis.py
│   └── evacuation\_shelters.py
│
├── utils/
│   ├── api\_client.py             # Open-Meteo and OSM Overpass calls
│   ├── prediction\_pipeline.py    # Model loading and inference
│   ├── path\_extrapolation.py     # Linear extrapolation for path prediction
│   ├── map\_builder.py            # Folium map construction
│   └── data\_processor.py        # Feature engineering
│
├── scripts/
│   ├── download\_data.py
│   ├── preprocess.py
│   ├── train\_all.py
│   ├── train\_rainfall\_rf.py
│   ├── train\_wind\_xgb.py
│   ├── train\_risk\_rf.py
│   └── verify\_models.py
│
└── notebooks/
    ├── 01\_data\_exploration.ipynb
    ├── 02\_feature\_engineering.ipynb
    ├── 03\_rainfall\_model.ipynb
    ├── 04\_wind\_model.ipynb
    ├── 05\_risk\_classifier.ipynb
    └── 06\_path\_prediction.ipynb
```

\---

## Tech Stack

|Category|Tools|
|-|-|
|Framework|Python 3.11, Streamlit 1.32|
|Data Processing|Pandas, NumPy, Scikit-learn|
|Machine Learning|Scikit-learn (Random Forest), XGBoost|
|Visualisation|Plotly Express, Folium (Leaflet.js), Matplotlib|
|Live APIs|Open-Meteo, OSM Overpass, NOAA IBTrACS|
|Deployment|Streamlit Cloud, GitHub|

\---

## Known Limitations

**API dependency** — Live weather and shelter data require an active internet connection. If Open-Meteo or the Overpass API is unreachable, the dashboard falls back to cached data.

**Data imbalance** — IBTrACS contains many weak storms (Depressions, Cyclonic Storms) but very few intense ones (Extremely Severe, Super Cyclonic). The risk classifier uses `class\_weight=balanced` to partially compensate, but rare extreme events are still underrepresented in training.

**Prediction horizon** — Path extrapolation accuracy degrades beyond 24 hours. The wind and rainfall models are not designed for multi-day lead times.

**Geographic scope** — The dashboard is built and tested for Indian coastal cities. The Bay of Bengal basin has the most training data; Arabian Sea coverage is thinner.

**Computational constraints** — Advanced numerical weather models (GraphCast, Pangu-Weather) were not included because they require GPU infrastructure and significant inference time that is not compatible with a real-time web app.

\---

## Acknowledgements

* [NOAA NCEI](https://www.ncei.noaa.gov/) for maintaining the IBTrACS dataset
* [India Meteorological Department](https://mausam.imd.gov.in/) for cyclone track advisories
* [Open-Meteo](https://open-meteo.com/) for providing a free, open weather API
* [OpenStreetMap](https://www.openstreetmap.org/) contributors for shelter data via the Overpass API
* IIIT Hyderabad for academic support and infrastructure

