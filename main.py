from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import traceback
import natal
import ephemeris
import advisor

print("🔥 NEW MAIN.PY IS RUNNING 🔥")
app = FastAPI()
from pathlib import Path

@app.get("/debug")
def debug():
    return {
        "debug": "NEW_VERSION_2026_09_02",
        "commit": Path("deployed_commit.txt").read_text().strip(),
        "cwd": str(Path.cwd()),
        "main_file": __file__,
        "natal_exists": Path("natal.py").exists(),
        "ephemeris_exists": Path("ephemeris.py").exists(),
        "natal": str(Path("natal.py").resolve()),
        "ephemeris": str(Path("ephemeris.py").resolve()),
    }
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
