import pickle
import os

files = [
    "rainfall_model_meta.pkl",
    "wind_model_meta.pkl",
    "risk_model_meta.pkl",
    "path_prediction.pkl"
]

for f in files:
    if os.path.exists(f):
        with open(f, "rb") as fh:
            try:
                data = pickle.load(fh)
                print(f"{f}: Type={type(data)}, Keys={list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                if not isinstance(data, dict):
                    print(f"  WARNING: {f} is NOT a dict!")
            except Exception as e:
                print(f"{f}: ERROR {e}")
    else:
        print(f"{f}: MISSING")
