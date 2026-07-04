import json
import os
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json_db(filename: str) -> Dict[str, Any]:
    """Loads a JSON file from the database directory."""
    path = os.path.join(BASE_DIR, filename)
    with open(path, 'r') as file:
        return json.load(file)

NISAB_DATA = load_json_db('nisab.json')
HAD_KIFAYAH_DATA = load_json_db('had_kifayah.json')

# Zakat rate is a fixed constant
ZAKAT_RATE = 0.025