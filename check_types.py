from prediction_pipeline import load_models
import pickle

models = load_models()
print(f"Type of models['rainfall']: {type(models.get('rainfall'))}")
print(f"Type of models['rainfall_meta']: {type(models.get('rainfall_meta'))}")

with open('rainfall_model_meta.pkl', 'rb') as f:
    data = pickle.load(f)
    print(f"Loaded from file type: {type(data)}")
    print(f"Loaded data: {data}")
