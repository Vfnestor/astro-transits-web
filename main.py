from pathlib import Path
import traceback

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import natal
import ephemeris
import advisor


print("🔥 ASTRO TRANSITS — NEW MAIN.PY 🔥")


app = FastAPI(
    title="Astro Vahid",
    description="Personal Astrology Dashboard",
    version="1.1.0",
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status":
            "ok",

        "service":
            "astro-transits",
    }


# =========================================================
# DEBUG
# =========================================================

@app.get("/debug")
def debug():

    commit_file = Path(
        "deployed_commit.txt"
    )

    return {

        "debug":
            "ASTRO_VERSION_3_0_0",

        "commit":
            (
                commit_file.read_text(
                    encoding="utf-8"
                ).strip()

                if commit_file.exists()

                else "unknown"
            ),

        "cwd":
            str(
                Path.cwd()
            ),

        "main_file":
            str(
                Path(__file__).resolve()
            ),

        "natal_exists":
            Path(
                "natal.py"
            ).exists(),

        "ephemeris_exists":
            Path(
                "ephemeris.py"
            ).exists(),

        "advisor_exists":
            Path(
                "advisor.py"
            ).exists(),

        "ephe_exists":
            Path(
                "ephe"
            ).exists(),
    }


# =========================================================
# HOME
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def root():

    index_file = Path(
        "index.html"
    )

    if not index_file.exists():

        return HTMLResponse(
            "<h1>index.html پیدا نشد.</h1>",
            status_code=500
        )

    return HTMLResponse(
        index_file.read_text(
            encoding="utf-8"
        )
    )


# =========================================================
# NATAL
# =========================================================

@app.get("/natal")
def get_natal():

    try:

        return (
            natal.get_natal_chart()
        )

    except Exception as e:

        return {
            "error":
                str(e),

            "trace":
                traceback.format_exc(),
        }


# =========================================================
# TRANSITS
# =========================================================

@app.get("/transits")
def get_transits():

    try:

        return (
            ephemeris.get_today_transits()
        )

    except Exception as e:

        return {
            "error":
                str(e),

            "trace":
                traceback.format_exc(),
        }


# =========================================================
# ANALYSIS
# =========================================================

@app.get("/analysis")
def get_analysis():

    try:

        natal_chart = (
            natal.get_natal_chart()
        )

        transit_data = (
            ephemeris.get_today_transits()
        )

        return {

            "status":
                "ok",

            "natal":
                natal_chart,

            "transits":
                transit_data,
        }

    except Exception as e:

        return {

            "error":
                str(e),

            "trace":
                traceback.format_exc(),
        }


# =========================================================
# ADVISOR
# =========================================================

@app.post("/advisor")
def ask_advisor(
    data: dict
):

    try:

        question = (
            data.get(
                "question",
                ""
            )
            .strip()
        )

        history = (
            data.get(
                "history",
                []
            )
        )

        if not question:

            return {
                "status":
                    "error",

                "message":
                    "لطفاً سؤال خود را وارد کنید.",
            }

        if not isinstance(
            history,
            list
        ):

            history = []

        # جلوگیری از ارسال تاریخچه بسیار بزرگ
        history = history[-12:]

        result = advisor.get_advice(
            question,
            history
        )

        return result

    except Exception as e:

        print(
            "ADVISOR ENDPOINT ERROR:",
            repr(e)
        )

        return {

            "status":
                "error",

            "message":
                "خطا در ارتباط با مشاور.",

            "debug":
                str(e),

            "trace":
                traceback.format_exc(),
        }
