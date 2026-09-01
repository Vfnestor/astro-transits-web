from pydantic import BaseModel
from ephemeris import detect_aspects

class AdvisorQuestion(BaseModel):
    question: str
    topic: str | None = None

class AdvisorAnswer(BaseModel):
    question: str
    summary: str
    advice: str
    aspects: list

def infer_topic(q):
    q = q.lower()
    if "کار" in q or "شغل" in q:
        return "career"
    if "رابطه" in q or "عشق" in q:
        return "relationship"
    if "خانه" in q or "مهاجرت" in q:
        return "home"
    if "روان" in q or "استرس" in q:
        return "inner"
    return "general"

def build_advice(topic, aspects):
    text = []

    if topic == "career":
        text.append("تمرکز روی خانه‌های ۱۰، ۶، ۲ و ۱ است.")
    elif topic == "relationship":
        text.append("تمرکز روی خانه‌های ۷، ۵ و ۱ است.")
    elif topic == "home":
        text.append("تمرکز روی خانه‌های ۴، ۱۰ و ۱ است.")
    elif topic == "inner":
        text.append("تمرکز روی خانه‌های ۸، ۱۲ و ۴ است.")
    else:
        text.append("سؤال کلی است و چند محور را فعال می‌کند.")

    if not aspects:
        text.append("ترانزیت سنگینی روی نقاط حساس دیده نمی‌شود.")
    else:
        text.append("ترانزیت‌های مهم:")
        for asp in aspects:
            text.append(f"- {asp['transit']} {asp['aspect']} با {asp['natal']} (اورب {asp['orb']})")

    return "\n".join(text)
