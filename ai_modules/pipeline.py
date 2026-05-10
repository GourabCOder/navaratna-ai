from ai_modules import numerology_engine
from ai_modules import astrology_engine
from ai_modules import gemstone_recommender

def generate_prediction(name: str, dob: str, gender: str, weight: str, zodiac: str, problem: str) -> dict:
    """
    Main pipeline integrating numerology, astrology, predicting gemstones,
    and generating an explanation using RAG.
    """
    # 1. Numerology
    life_path = numerology_engine.calculate_life_path_number(dob)
    
    # 2. Astrology Zodiac (Fallback to engine if zodiac not provided or to ensure accuracy)
    # The instructions say calculate it from DOB
    zodiac_sign = astrology_engine.get_zodiac_from_dob(dob)
    
    # 3. Ruling Planet
    planet = astrology_engine.get_ruling_planet(zodiac_sign)
    
    # 4. Gemstone Recommendation
    gemstone = gemstone_recommender.recommend_gemstone(life_path, planet)
    
    # 5. Explanation Generation (No RAG)
    explanation = f"Based on your life path {life_path} and {zodiac_sign} energy, {gemstone} is recommended to overcome '{problem}'."
    prediction_text = f"Your cosmic path reveals profound potential. By honoring {planet}, you will overcome your current challenges."
    
    return {
        "life_path_number": life_path,
        "zodiac_sign": zodiac_sign,
        "dominant_planet": planet,
        "recommended_gemstone": gemstone,
        "prediction": prediction_text,
        "explanation": explanation
    }
