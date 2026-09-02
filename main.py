from pathlib import Path
import traceback

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import natal
import ephemeris
import advisor


print("🔥 ASTRO TRANSITS - NEW VERSION 🔥")


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="مشاور نجومی شخصی",
    version="1.0.0",
)


# =========================================================
# Static files
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# =========================================================
# Home
# =========================================================

@app.get("/", response_class=HTMLResponse)
def root():
    index_file = BASE_DIR / "index.html"

    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


# =========================================================
# Health
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "astro-transits",
        "version": "1.0.0",
    }


# =========================================================
# Debug
# =========================================================

@app.get("/debug")
def debug():
    commit_file = BASE_DIR / "deployed_commit.txt"

    commit = ""

    if commit_file.exists():
        commit = commit_file.read_text(
            encoding="utf-8"
        ).strip()

    return {
        "debug": "ASTRO_VERSION_1_0_0",
        "commit": commit,
        "cwd": str(Path.cwd()),
        "main_file": str(Path(__file__).resolve()),
        "natal_exists": (BASE_DIR / "natal.py").exists(),
        "ephemeris_exists": (BASE_DIR / "ephemeris.py").exists(),
        "advisor_exists": (BASE_DIR / "advisor.py").exists(),
        "ephe_exists": (BASE_DIR / "ephe").exists(),
    }


# =========================================================
# Natal chart
# =========================================================

@app.get("/natal")
def get_natal():

    try:
        return natal.get_natal_chart()

    except Exception as e:

        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }


# =========================================================
# Current transits
# =========================================================

@app.get("/transits")
def get_transits():

    try:
        return ephemeris.get_today_transits()

    except Exception as e:

        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }


# =========================================================
# Full astrological analysis
# =========================================================

@app.get("/analysis")
def get_analysis():

    try:
        return ephemeris.get_full_transit_analysis()

    except Exception as e:

        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }


# =========================================================
# Advisor
# =========================================================

@app.post("/advisor")
def ask_advisor(data: dict):

    try:

        question = str(
            data.get("question", "")
        ).strip()

        if not question:

            return {
                "status": "error",
                "error": "سؤال خالی است.",
            }

        return {
            "status": "ok",
            "advice": advisor.get_advice(question),
        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }
