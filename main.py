from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import natal
import ephemeris
import advisor

app = FastAPI()

# ---------------- CORS FIX ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # می‌تونی بعداً فقط دامنهٔ فرانت‌اند رو بزاری
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {
        "message": "0.4 - سرور نجومی فعال است",
        "time": datetime.now()
    }

# ---------------- NATAL ----------------
@app.get("/natal")
def get_natal():
    return natal.get_natal_chart()

# ---------------- TRANSITS ----------------
@app.get("/transits")
def get_transits():
    return ephemeris.get_today_transits()

# ---------------- ADVISOR ----------------
@app.post("/advisor")
def ask_advisor(data: dict):
    question = data.get("question", "")
    return {"advice": advisor.get_advice(question)}
