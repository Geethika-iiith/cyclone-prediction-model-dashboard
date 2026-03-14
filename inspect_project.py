import pandas as pd
import pickle
import os

base = r'c:\Users\geeth\Downloads\New folder\CycloneDashboard\CycloneDashboard'

with open(os.path.join(base, 'inspection_output.txt'), 'w') as f:
    # Rainfall features
    df = pd.read_csv(os.path.join(base, 'data', 'ml_rainfall_features.csv'), nrows=3)
    f.write('=== ml_rainfall_features.csv ===\n')
    f.write(f'Columns: {list(df.columns)}\n')
    f.write(f'Sample:\n{df.head().to_string()}\n\n')

    # Wind features
    df = pd.read_csv(os.path.join(base, 'data', 'ml_wind_features.csv'), nrows=3)
    f.write('=== ml_wind_features.csv ===\n')
    f.write(f'Columns: {list(df.columns)}\n')
    f.write(f'Sample:\n{df.head().to_string()}\n\n')

    # Risk features
    df = pd.read_csv(os.path.join(base, 'data', 'ml_risk_features.csv'), nrows=3)
    f.write('=== ml_risk_features.csv ===\n')
    f.write(f'Columns: {list(df.columns)}\n')
    f.write(f'Sample:\n{df.head().to_string()}\n\n')

    # Cities expanded
    df = pd.read_csv(os.path.join(base, 'data', 'data_cities_expanded.csv'))
    f.write('=== data_cities_expanded.csv ===\n')
    f.write(f'Columns: {list(df.columns)}\n')
    f.write(f'{df.to_string()}\n\n')

    # City population
    df = pd.read_csv(os.path.join(base, 'city_population.csv'))
    f.write('=== city_population.csv ===\n')
    f.write(f'{df.to_string()}\n\n')

    # Rainfall data (shelters)
    df = pd.read_csv(os.path.join(base, 'rainfall_data.csv'))
    f.write('=== rainfall_data.csv ===\n')
    f.write(f'{df.to_string()}\n\n')

    # Weather daily
    df = pd.read_csv(os.path.join(base, 'data', 'weather_daily_all_cities.csv'), nrows=3)
    f.write('=== weather_daily_all_cities.csv ===\n')
    f.write(f'Columns: {list(df.columns)}\n')
    f.write(f'Sample:\n{df.head().to_string()}\n\n')

    # Load models one by one
    for m in os.listdir(os.path.join(base, 'models')):
        fp = os.path.join(base, 'models', m)
        f.write(f'=== {m} (size: {os.path.getsize(fp)} bytes) ===\n')
        try:
            obj = pickle.load(open(fp, 'rb'))
            f.write(f'Type: {type(obj)}\n')
            if hasattr(obj, 'feature_names_in_'):
                f.write(f'Features: {list(obj.feature_names_in_)}\n')
            if hasattr(obj, 'n_features_in_'):
                f.write(f'N features: {obj.n_features_in_}\n')
            if hasattr(obj, 'classes_'):
                f.write(f'Classes: {list(obj.classes_)}\n')
            if isinstance(obj, dict):
                f.write(f'Keys: {list(obj.keys())}\n')
                f.write(f'Content: {obj}\n')
            elif isinstance(obj, (list, tuple)):
                f.write(f'Content: {obj}\n')
            elif not hasattr(obj, 'predict'):
                f.write(f'Content: {obj}\n')
        except Exception as e:
            f.write(f'ERROR loading: {e}\n')
        f.write('\n')

print("Done! Check inspection_output.txt")
