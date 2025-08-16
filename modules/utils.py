import json
from config import DATA_PATH

def load_json(filename):
    try:
        with open(DATA_PATH + filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(DATA_PATH + filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
