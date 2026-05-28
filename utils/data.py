import json, os



def ensure_dir(): os.mkdirs('../data', exist_ok=True)

def load_data(filename: str):
    ensure_dir()
    try:
        with open(f'../data/{filename}', 'r') as f: data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Creating data entry, '{filename}'.")
        return {}

def save_data(filename:str, data: dict):
    ensure_dir()
    with open(f'../data/{filename}', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved data in data entry, '{filename}'.")
