"""
retrain_models.py
-----------------
Retrains all ML models from existing feature CSVs and saves them as .pkl files.
Models:
  1. Rainfall Intensity  — RandomForestRegressor
  2. Wind Speed          — XGBRegressor (Gradient Boosting)
  3. Risk Level          — RandomForestClassifier
  4. Path Prediction     — Linear extrapolation (metadata only)
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, accuracy_score
)
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
MODELS = os.path.join(BASE, "models")
os.makedirs(MODELS, exist_ok=True)


# ─────────────────────── 1. RAINFALL MODEL ───────────────────────
def train_rainfall_model():
    print("=" * 60)
    print("Training Rainfall Intensity Model (RandomForestRegressor)")
    print("=" * 60)

    df = pd.read_csv(os.path.join(DATA, "ml_rainfall_features.csv"))
    features = [
        "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
        "windspeed_10m_max", "windgusts_10m_max", "precipitation_hours",
        "rain_lag_1d", "rain_lag_3d", "rain_lag_7d",
        "wind_change", "temp_change", "month", "is_cyclone_season",
    ]
    target = "rain_sum"

    df = df.dropna(subset=features + [target])
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200, max_depth=15, min_samples_split=5,
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"  RMSE : {rmse:.4f}")
    print(f"  MAE  : {mae:.4f}")
    print(f"  R²   : {r2:.4f}")

    pickle.dump(model, open(os.path.join(MODELS, "rainfall_model.pkl"), "wb"))
    pickle.dump(
        {"features": features, "rmse": rmse, "mae": mae, "r2": r2},
        open(os.path.join(MODELS, "rainfall_model_meta.pkl"), "wb"),
    )
    print("  ✓ Saved rainfall_model.pkl & rainfall_model_meta.pkl\n")


# ─────────────────────── 2. WIND SPEED MODEL ────────────────────
def train_wind_model():
    print("=" * 60)
    print("Training Wind Speed Model (XGBRegressor)")
    print("=" * 60)

    df = pd.read_csv(os.path.join(DATA, "ml_wind_features.csv"))
    features = [
        "pressure_mb", "pressure_change", "category_num",
        "LAT", "LON", "lat_change", "lon_change",
        "month", "dist_to_land_km",
    ]
    target = "wind_kmh"

    df = df.dropna(subset=features + [target])
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=300, max_depth=8, learning_rate=0.1,
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"  RMSE : {rmse:.4f}")
    print(f"  R²   : {r2:.4f}")

    pickle.dump(model, open(os.path.join(MODELS, "wind_model.pkl"), "wb"))
    pickle.dump(
        {"features": features, "rmse": rmse, "r2": r2},
        open(os.path.join(MODELS, "wind_model_meta.pkl"), "wb"),
    )
    print("  ✓ Saved wind_model.pkl & wind_model_meta.pkl\n")


# ─────────────────────── 3. RISK CLASSIFIER ─────────────────────
def train_risk_classifier():
    print("=" * 60)
    print("Training Risk Level Classifier (RandomForestClassifier)")
    print("=" * 60)

    df = pd.read_csv(os.path.join(DATA, "ml_risk_features.csv"))
    features = [
        "wind_kmh", "pressure_mb", "distance_km", "population_density",
    ]
    target = "risk_level"

    df = df.dropna(subset=features + [target])
    X = df[features]
    y = df[target]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_split=5,
        random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Classes  : {list(le.classes_)}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    pickle.dump(model, open(os.path.join(MODELS, "risk_classifier.pkl"), "wb"))
    pickle.dump(le, open(os.path.join(MODELS, "risk_label_encoder.pkl"), "wb"))
    pickle.dump(
        {"features": features, "accuracy": acc, "classes": list(le.classes_)},
        open(os.path.join(MODELS, "risk_model_meta.pkl"), "wb"),
    )
    print("  ✓ Saved risk_classifier.pkl, risk_label_encoder.pkl & risk_model_meta.pkl\n")


# ─────────────────────── 4. PATH PREDICTION META ────────────────
def save_path_prediction_meta():
    print("=" * 60)
    print("Saving Path Prediction Metadata (Linear Extrapolation)")
    print("=" * 60)
    meta = {
        "method": "linear_extrapolation",
        "lookback": 4,
        "mean_error_km": 23.37,
        "median_error_km": 16.71,
    }
    pickle.dump(meta, open(os.path.join(MODELS, "path_prediction.pkl"), "wb"))
    print("  ✓ Saved path_prediction.pkl\n")


if __name__ == "__main__":
    train_rainfall_model()
    train_wind_model()
    train_risk_classifier()
    save_path_prediction_meta()
    print("✅ All models retrained and saved successfully!")
