import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, 'knowledge_base')

def recommend_gemstone(life_path: int, planet: str) -> str:
    """
    Recommends a gemstone based on the ruling planet (and life path number if needed).
    """
    map_path = os.path.join(KB_DIR, 'planet_gemstone_map.json')
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Unknown"
        
    planet_map = data.get("planet_gemstone_mapping", {})
    gemstone = planet_map.get(planet, "Unknown")
    
    return gemstone
