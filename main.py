from pathlib import Path
import base64
import hashlib
import hmac
import json
import os
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import natal
import ephemeris
import advisor


print("🔥 ASTRO TRANSITS — AI ADVISOR VERSION 🔥")


app = FastAPI(
    title="Astro Vahid",
    description="Personal Astrology Dashboard",
    version="2.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# ============================================================
# SESSION / ADVISOR NAME
# ============================================================

SESSION_COOKIE = "astro_session"

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "dev-only-change-this-secret",
).encode("utf-8")


def _sign(payload):
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    encoded = base64.urlsafe_b64encode(
        raw
    ).decode("ascii")

    signature = hmac.new(
        SESSION_SECRET,
        encoded.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()

    return f"{encoded}.{signature}"


def _read_session(request: Request):
    value = request.cookies.get(
        SESSION_COOKIE
    )

    if not value or "." not in value:
        return None

    encoded, signature = value.rsplit(
        ".",
        1,
    )

    expected = hmac.new(
        SESSION_SECRET,
        encoded.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        signature,
        expected,
    ):
        return None

    try:
        raw = base64.urlsafe_b64decode(
            encoded.encode("ascii")
        )

        return json.loads(
            raw.decode("utf-8")
        )

    except Exception:
        return None


def _set_session(response, data):
    response.set_cookie(
        key=SESSION_COOKIE,
        value=_sign(data),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,
    )


# ============================================================
# PROFILE MODEL
# ============================================================

class Profile(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    family_name: str = Field(
        min_length=1,
        max_length=100,
    )

    advisor_name: str = Field(
        min_length=1,
        max_length=80,
    )

    birth_date: str

    birth_time: str

    city: str = Field(
        min_length=1,
        max_length=120,
    )

    latitude: float

    longitude: float

    utc_offset: float


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "astro-transits",
        "ai": bool(
            os.getenv("OPENAI_API_KEY")
        ),
        "model": advisor.MODEL,
    }


# ============================================================
# DEBUG
# ============================================================

@app.get("/debug")
def debug():
    commit_file = Path(
        "deployed_commit.txt"
    )

    return {
        "debug": "ASTRO_AI_VERSION_2_0_0",

        "commit": (
            commit_file.read_text(
                encoding="utf-8"
            ).strip()
            if commit_file.exists()
            else "unknown"
        ),

        "cwd": str(Path.cwd()),

        "main_file": str(
            Path(__file__).resolve()
        ),

        "natal_exists": Path(
            "natal.py"
        ).exists(),

        "ephemeris_exists": Path(
            "ephemeris.py"
        ).exists(),

        "advisor_exists": Path(
            "advisor.py"
        ).exists(),

        "ephe_exists": Path(
            "ephe"
        ).exists(),

        "openai_key": bool(
            os.getenv(
                "OPENAI_API_KEY"
            )
        ),

        "openai_model": advisor.MODEL,
    }


# ============================================================
# HOME
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
def root():
    index_file = Path(
        "index.html"
    )

    if not index_file.exists():
        return HTMLResponse(
            "<h1>index.html پیدا نشد.</h1>",
            status_code=500,
        )

    return HTMLResponse(
        index_file.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# PROFILE
# ============================================================

@app.post("/profile")
def save_profile(
    profile: Profile,
    request: Request,
):
    try:
        data = profile.model_dump()

        # Validate chart before changing session.
        chart = natal.get_natal_chart(
            data
        )

        old_session = _read_session(
            request
        )

        requested_name = (
            data["advisor_name"]
            .strip()
        )

        if old_session is None:
            session = {
                "advisor_name":
                    requested_name,

                "name_changes": 0,

                "name_locked": False,
            }

        else:
            current_name = (
                old_session.get(
                    "advisor_name",
                    "",
                )
            )

            changes = int(
                old_session.get(
                    "name_changes",
                    0,
                )
            )

            locked = bool(
                old_session.get(
                    "name_locked",
                    False,
                )
            )

            if requested_name != current_name:

                if locked or changes >= 3:
                    return {
                        "status": "error",
                        "message": (
                            "نام مشاور قبلاً "
                            "۳ بار تغییر کرده و "
                            "اکنون قفل شده است."
                        ),
                        "advisor_name":
                            current_name,

                        "name_changes":
                            changes,

                        "name_changes_remaining":
                            0,

                        "name_locked": True,
                    }

                changes += 1

                current_name = (
                    requested_name
                )

                if changes >= 3:
                    locked = True

            session = {
                "advisor_name":
                    current_name,

                "name_changes":
                    changes,

                "name_locked":
                    locked,
            }

            data["advisor_name"] = (
                current_name
            )

        from fastapi.responses import JSONResponse

        response = JSONResponse({
            "status": "ok",

            "profile": {
                **data,
                "advisor_name":
                    session[
                        "advisor_name"
                    ],
            },

            "advisor_name":
                session[
                    "advisor_name"
                ],

            "name_changes":
                session[
                    "name_changes"
                ],

            "name_changes_remaining":
                max(
                    0,
                    3 - session[
                        "name_changes"
                    ],
                ),

            "name_locked":
                session[
                    "name_locked"
                ],

            "natal": chart,
        })

        _set_session(
            response,
            session,
        )

        return response

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
        }


# ============================================================
# NATAL
# ============================================================

@app.post("/natal")
def get_natal(profile: Profile):
    try:
        return natal.get_natal_chart(
            profile.model_dump()
        )

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
        }


# ============================================================
# TRANSITS / ANALYSIS
# ============================================================

@app.post("/analysis")
def get_analysis(profile: Profile):
    try:
        profile_data = profile.model_dump()

        natal_chart = natal.get_natal_chart(
            profile_data
        )

        transit_data = (
            ephemeris.get_today_transits()
        )

        return {
            "status": "ok",
            "natal": natal_chart,
            "transits": transit_data,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
        }


@app.get("/transits")
def get_transits():
    try:
        return ephemeris.get_today_transits()

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
        }


# ============================================================
# AI ADVISOR
# ============================================================

@app.post("/advisor")
def ask_advisor(
    data: dict,
    request: Request,
):
    try:
        question = str(
            data.get(
                "question",
                "",
            )
        ).strip()

        history = data.get(
            "history",
            [],
        )

        profile_data = data.get(
            "profile"
        )

        if not question:
            return {
                "status": "error",
                "message":
                    "لطفاً سؤال خود را وارد کنید.",
            }

        if not isinstance(
            profile_data,
            dict,
        ):
            return {
                "status": "error",
                "message":
                    "ابتدا پروفایل خود را ذخیره کنید.",
            }

        session = _read_session(
            request
        )

        if not session:
            return {
                "status": "error",
                "message":
                    "ابتدا پروفایل را ذخیره کنید.",
            }

        # نام واقعی مشاور از session گرفته می‌شود.
        # مرورگر اجازه تغییر مستقیم آن را ندارد.
        profile_data[
            "advisor_name"
        ] = session[
            "advisor_name"
        ]

        result = advisor.get_advice(
            question=question,
            history=history,
            profile=profile_data,
        )

        return result

    except Exception as e:
        print(
            "ADVISOR ENDPOINT ERROR:",
            repr(e),
        )

        return {
            "status": "error",
            "message":
                "خطا در ارتباط با مشاور.",
            "debug": str(e),
            "trace":
                traceback.format_exc(),
        }
