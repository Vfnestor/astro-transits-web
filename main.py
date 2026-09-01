from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from natal import natal
from advisor import AdvisorQuestion, AdvisorAnswer, infer_topic, build_advice
from ephemeris import get_planet_positions, detect_aspects

app = FastAPI(
    title="Astro Advisor 0.4",
    description="نسخه کامل با اپهمریس واقعی + چارت تولد واقعی vahid",
    version="0.4"
)

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {
        "message": "سرور نجومی فعال است – نسخه 0.4",
        "time": datetime.now().isoformat()
    }

# -------------------- NATAL --------------------
@app.get("/natal")
def get_natal():
    return natal

# -------------------- TRANSITS --------------------
@app.get("/transits")
def get_transits():
    now = datetime.now()

    # ترانزیت‌های واقعی امروز
    transit_positions = get_planet_positions(
        now.year, now.month, now.day, now.hour + now.minute/60
    )

    # موقعیت واقعی سیارات در لحظه تولد vahid
    natal_positions = get_planet_positions(
        natal.birth_year,
        natal.birth_month,
        natal.birth_day,
        natal.birth_hour
    )

    # زوایا
    aspects = detect_aspects(natal_positions, transit_positions)

    return {
        "timestamp": now.isoformat(),
        "transits": transit_positions,
        "natal_positions": natal_positions,
        "aspects": aspects
    }

# -------------------- ADVISOR --------------------
@app.post("/advisor", response_model=AdvisorAnswer)
def advisor_endpoint(q: AdvisorQuestion):

    topic = infer_topic(q.question)

    now = datetime.now()

    # ترانزیت‌های واقعی امروز
    transit_positions = get_planet_positions(
        now.year, now.month, now.day, now.hour + now.minute/60
    )

    # موقعیت واقعی سیارات تولد vahid
    natal_positions = get_planet_positions(
        natal.birth_year,
        natal.birth_month,
        natal.birth_day,
        natal.birth_hour
    )

    # زوایا
    aspects = detect_aspects(natal_positions, transit_positions)

    # متن مشاوره
    advice_text = build_advice(topic, aspects)

    return AdvisorAnswer(
        question=q.question,
        summary="تحلیل بر اساس چارت تولد واقعی vahid + ترانزیت‌های واقعی امروز",
        advice=advice_text,
        aspects=aspects
    )
