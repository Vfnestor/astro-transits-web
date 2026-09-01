from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import natal
import ephemeris
import advisor

app = FastAPI()

# سرو کردن فایل‌های استاتیک مثل CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------- ROOT: سرو کردن index.html ----------------
@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

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
