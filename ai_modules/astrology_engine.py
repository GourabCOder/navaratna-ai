import json
import os
import datetime

# Get the path to the knowledge base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, 'knowledge_base')

def get_zodiac_from_dob(dob: str) -> str:
    """
    Returns the zodiac sign based on the Date of Birth.
    Handles multiple formats gracefully.
    """
    try:
        # Try primary format
        if '-' in dob:
            date_obj = datetime.datetime.strptime(dob, "%Y-%m-%d")
        elif '/' in dob:
            date_obj = datetime.datetime.strptime(dob, "%d/%m/%Y")
        else:
            # Fallback Date parsing or if it's just raw numbers
            raise ValueError
    except ValueError:
        # Fallback date if parsing completely fails so the UI doesn't crash
        date_obj = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d")

    month = date_obj.month
    day = date_obj.day
        
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
        
    return "Unknown"

def get_ruling_planet(zodiac: str) -> str:
    """
    Returns the ruling planet for a given zodiac sign.
    Loads mapping from knowledge_base/planet_gemstone_map.json
    Normalizes input to Title Case.
    """
    if not zodiac:
        return "Unknown"
        
    zodiac_normalized = zodiac.strip().title()
    
    map_path = os.path.join(KB_DIR, 'planet_gemstone_map.json')
    try:
        with open(map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Unknown"
        
    zodiac_map = data.get("zodiac_planet_mapping", {})
    return zodiac_map.get(zodiac_normalized, "Unknown")
