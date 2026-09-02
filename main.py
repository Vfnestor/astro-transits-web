from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import traceback
import natal
import ephemeris
import advisor

@app.get("/debug")
def debug():
    import natal
    import ephemeris
    return {
        "natal_file": natal.__file__,
        "ephemeris_file": ephemeris.__file__,
    }
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/natal")
def get_natal():
    try:
        return natal.get_natal_chart()
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/transits")
def get_transits():
    try:
        return ephemeris.get_today_transits()
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

@app.post("/advisor")
def ask_advisor(data: dict):
    try:
        question = data.get("question", "")
        return {"advice": advisor.get_advice(question)}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
