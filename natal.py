from datetime import datetime

# نمونهٔ ساده و بدون خطا برای چارت تولد
# می‌تونی بعداً با محاسبات واقعی جایگزینش کنی

def get_natal_chart():
    # خروجی باید ۱۰۰٪ JSON معتبر باشد
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
