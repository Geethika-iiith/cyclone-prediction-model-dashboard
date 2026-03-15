import pickle
import os

for f in ["rainfall_model_meta.pkl", "wind_model_meta.pkl", "risk_model_meta.pkl"]:
    with open(f, 'rb') as fh:
        obj = pickle.load(fh)
        print(f"--- {f} ---")
        print(f"Type: {type(obj)}")
        if isinstance(obj, dict):
            print(f"Keys: {list(obj.keys())}")
        else:
            print("NOT A DICT")
