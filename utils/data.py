import json, os



def _ensure_dir(): os.mkdirs('../data', exist_ok=True)

def load_data(filename: str):
    _ensure_dir()
    try:
        with open(f'../data/{filename}.json', 'r') as f: data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Creating new data entry: '{filename}'.")
        return {}

def save_data(filename:str, data: dict):
    _ensure_dir()
    with open(f'../data/{filename}.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated data in data entry: '{filename}'.")
