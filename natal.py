from datetime import datetime

def get_natal_chart():
    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "chart": {
            "sun": "Aries",
            "moon": "Cancer",
            "ascendant": "Leo",
            "planets": {
                "mercury": "Pisces",
                "venus": "Taurus",
                "mars": "Gemini",
                "jupiter": "Leo",
                "saturn": "Aquarius"
            }
        }
    }
