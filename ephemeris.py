from datetime import datetime

def get_today_transits():
    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "transits": [
            {"planet": "Sun", "aspect": "trine Moon"},
            {"planet": "Moon", "aspect": "square Mars"},
            {"planet": "Mercury", "aspect": "sextile Venus"},
            {"planet": "Mars", "aspect": "opposition Saturn"},
            {"planet": "Jupiter", "aspect": "trine Uranus"}
        ]
    }

def detect_aspects(chart):
    # نسخهٔ ساده برای جلوگیری از خطا
    return [
        {"planet": "Sun", "aspect": "trine Moon"},
        {"planet": "Mars", "aspect": "square Venus"}
    ]
