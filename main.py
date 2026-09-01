from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from natal import NatalChart
from advisor import AdvisorQuestion, AdvisorAnswer, infer_topic, build_advice
from ephemeris import get_planet_positions, detect_aspects
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# چارت تولد واقعی تو را اینجا وارد می‌کنیم
natal = NatalChart(
    birth_year=1998,
    birth_month=7,
    birth_day=12,
    birth_hour=14.5,
    lat=35.6892,
    lon=51.3890
)

@app.get("/natal")
def get_natal():
    return natal

@app.get("/transits")
def get_transits():
    now = datetime.now()
    transits = get_planet_positions(now.year, now.month, now.day)
    natal_positions = get_planet_positions(
        natal.birth_year, natal.birth_month, natal.birth_day, natal.birth_hour
    )
    aspects = detect_aspects(natal_positions, transits)
    return {
        "transits": transits,
        "aspects": aspects
    }

@app.post("/advisor")
def advisor(q: AdvisorQuestion):
    topic = infer_topic(q.question)
    now = datetime.now()
    transits = get_planet_positions(now.year, now.month, now.day)
    natal_positions = get_planet_positions(
        natal.birth_year, natal.birth_month, natal.birth_day, natal.birth_hour
    )
    aspects = detect_aspects(natal_positions, transits)
    advice = build_advice(topic, aspects)

    return AdvisorAnswer(
        question=q.question,
        summary=f"تحلیل بر اساس ترانزیت واقعی و چارت تولد.",
        advice=advice,
        aspects=aspects
    )
