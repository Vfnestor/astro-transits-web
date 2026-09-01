from datetime import datetime

# نمونهٔ ساده و بدون خطا برای ترانزیت‌های امروز
# می‌تونی بعداً با محاسبات واقعی جایگزینش کنی

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
