from ephemeris import detect_aspects
from datetime import datetime

def _interpret_aspect(aspect: dict):
    p1 = aspect["planet1"]
    p2 = aspect["planet2"]
    a = aspect["aspect"]

    if a == "trine":
        return f"هماهنگی مثبت بین {p1} و {p2}؛ زمان خوبی برای جریان طبیعی امور است."
    if a == "square":
        return f"تنش بین {p1} و {p2}؛ نیاز به احتیاط و صبر در تصمیم‌گیری."
    if a == "opposition":
        return f"دوگانگی بین {p1} و {p2}؛ بهتر است قبل از اقدام، همه‌چیز را دوباره بررسی کنی."
    if a == "sextile":
        return f"فرصت نرم و قابل استفاده بین {p1} و {p2}؛ اگر حرکت کنی، حمایت می‌گیری."
    if a == "conjunction":
        return f"تمرکز انرژی روی محور {p1} و {p2}؛ این حوزه الان برجسته شده."

    return f"آسپکت {a} بین {p1} و {p2}؛ نیاز به توجه بیشتر."


def get_advice(question: str):
    aspects = detect_aspects(None)

    if not aspects:
        return (
            f"در حال حاضر ترانزیت برجسته‌ای ثبت نشده، "
            f"پس بهتر است در مورد «{question}» با آرامش و بر اساس منطق خودت تصمیم بگیری."
        )

    interpretations = [_interpret_aspect(a) for a in aspects[:5]]

    return (
        f"سوالت: «{question}»\n"
        f"بر اساس ترانزیت‌های فعلی:\n- "
        + "\n- ".join(interpretations)
        + "\nجمع‌بندی: این ترانزیت‌ها نشان می‌دهند که بهتر است هم احساس و هم منطق را کنار هم ببینی."
    )
