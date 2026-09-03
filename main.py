"main.py"

from pathlib import Path
import base64
import hashlib
import hmac
import json
import os
import traceback
import uuid

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from PIL import Image, ImageOps

import natal
import ephemeris
import advisor


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

PROFILE_STORAGE_DIR = Path(
    os.getenv(
        "PROFILE_STORAGE_DIR",
        str(BASE_DIR / "data" / "astro_profiles")
    )
)

PROFILE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

PHOTO_DIR = PROFILE_STORAGE_DIR / "photos"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Astro Transits",
    version="3.0.0",
    description="Personal AI Astrology Advisor"
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# =========================================================
# SESSION
# =========================================================

SESSION_COOKIE = "astro_session"

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "CHANGE_THIS_SECRET_IN_RENDER"
).encode("utf-8")


def _encode_session(data: dict) -> str:
    raw = json.dumps(
        data,
        ensure_ascii=False,
        separators=(",", ":")
    ).encode("utf-8")

    encoded = base64.urlsafe_b64encode(raw).decode("ascii")

    signature = hmac.new(
        SESSION_SECRET,
        encoded.encode("ascii"),
        hashlib.sha256
    ).hexdigest()

    return f"{encoded}.{signature}"


def _decode_session(value: str):
    if not value or "." not in value:
        return None

    try:
        encoded, signature = value.rsplit(".", 1)

        expected = hmac.new(
            SESSION_SECRET,
            encoded.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            return None

        raw = base64.urlsafe_b64decode(
            encoded.encode("ascii")
        )

        return json.loads(raw.decode("utf-8"))

    except Exception:
        return None


def get_session(request: Request):
    value = request.cookies.get(SESSION_COOKIE)

    if not value:
        return None

    return _decode_session(value)


def set_session(response, session: dict, request: Request):
    response.set_cookie(
        key=SESSION_COOKIE,
        value=_encode_session(session),
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=60 * 60 * 24 * 365,
        path="/"
    )


# =========================================================
# PROFILE STORAGE
# =========================================================

def profile_path(user_id: str) -> Path:
    return PROFILE_STORAGE_DIR / f"{user_id}.json"


def load_profile(user_id: str):
    path = profile_path(user_id)

    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return None


def save_profile_file(user_id: str, profile: dict):
    path = profile_path(user_id)

    temp = PROFILE_STORAGE_DIR / (
        f".{user_id}.{uuid.uuid4().hex}.tmp"
    )

    temp.write_text(
        json.dumps(
            profile,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    temp.replace(path)


# =========================================================
# PROFILE MODEL
# =========================================================

class Profile(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    family_name: str = Field(min_length=1, max_length=100)

    advisor_name: str = Field(
        min_length=1,
        max_length=80
    )

    birth_date: str
    birth_time: str

    city: str = Field(
        min_length=1,
        max_length=120
    )

    latitude: float
    longitude: float

    utc_offset: float


# =========================================================
# AVATAR
# =========================================================

def avatar_path(user_id: str) -> Path:
    return PHOTO_DIR / f"{user_id}.jpg"


def avatar_url(user_id: str):
    path = avatar_path(user_id)

    if not path.exists():
        return None

    try:
        version = int(path.stat().st_mtime)
    except Exception:
        version = 1

    return f"/profile/avatar/{user_id}.jpg?v={version}"


def delete_avatar(user_id: str):
    path = avatar_path(user_id)

    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass


async def optimize_avatar(upload: UploadFile, user_id: str):
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp",
    }

    if upload.content_type not in allowed_types:
        raise ValueError(
            "فرمت عکس مجاز نیست. JPG، PNG، WEBP یا GIF استفاده کنید."
        )

    content = await upload.read()

    # حداکثر حجم فایل خام: 10MB
    if len(content) > 10 * 1024 * 1024:
        raise ValueError(
            "حجم عکس نباید بیشتر از ۱۰ مگابایت باشد."
        )

    from io import BytesIO

    try:
        with Image.open(BytesIO(content)) as source:

            # اصلاح جهت عکس‌های موبایل
            source = ImageOps.exif_transpose(source)

            # تبدیل به RGB
            if source.mode in ("RGBA", "LA"):
                background = Image.new(
                    "RGB",
                    source.size,
                    (8, 11, 21)
                )

                alpha = source.getchannel("A")

                background.paste(
                    source.convert("RGB"),
                    mask=alpha
                )

                source = background

            else:
                source = source.convert("RGB")

            # برش مربعی و تغییر اندازه
            source = ImageOps.fit(
                source,
                (320, 320),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5)
            )

            output = avatar_path(user_id)

            source.save(
                output,
                "JPEG",
                quality=85,
                optimize=True,
                progressive=True
            )

            return output

    except Exception as exc:
        raise ValueError(
            f"پردازش تصویر ناموفق بود: {exc}"
        )


# =========================================================
# HOME
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    index_file = BASE_DIR / "index.html"

    if not index_file.exists():
        return HTMLResponse(
            "<h1>index.html پیدا نشد.</h1>",
            status_code=500
        )

    return HTMLResponse(
        index_file.read_text(encoding="utf-8")
    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "astro-transits",
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna"
        )
    }


@app.get("/debug")
async def debug():
    return {
        "status": "ok",
        "version": "3.0.0",
        "openai_key": bool(
            os.getenv("OPENAI_API_KEY")
        ),
        "openai_model": os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna"
        ),
        "profile_storage": str(
            PROFILE_STORAGE_DIR
        ),
        "photo_storage": str(
            PHOTO_DIR
        )
    }


# =========================================================
# CURRENT USER / LOGIN SESSION
# =========================================================

@app.get("/me")
async def me(request: Request):

    session = get_session(request)

    if not session:
        return {
            "status": "ok",
            "logged_in": False
        }

    user_id = session.get("user_id")

    if not user_id:
        return {
            "status": "ok",
            "logged_in": False
        }

    profile = load_profile(user_id)

    return {
        "status": "ok",
        "logged_in": bool(profile),
        "user_id": user_id,
        "profile": profile,
        "advisor_name": session.get(
            "advisor_name",
            profile.get("advisor_name") if profile else None
        ),
        "name_changes": session.get(
            "name_changes",
            0
        ),
        "name_changes_remaining": max(
            0,
            3 - int(session.get("name_changes", 0))
        ),
        "name_locked": bool(
            session.get("name_locked", False)
        ),
        "profile_image": avatar_url(user_id)
    }


# =========================================================
# SAVE PROFILE
# =========================================================

@app.post("/profile")
async def save_profile(
    profile: Profile,
    request: Request
):

    try:

        data = profile.model_dump()

        # بررسی اولیه چارت
        natal_chart = natal.get_natal_chart(data)

        session = get_session(request)

        # -----------------------------------------
        # New user
        # -----------------------------------------

        if not session:

            user_id = uuid.uuid4().hex

            session = {
                "user_id": user_id,
                "advisor_name": data["advisor_name"].strip(),
                "name_changes": 0,
                "name_locked": False
            }

        else:

            user_id = session.get("user_id")

            if not user_id:
                user_id = uuid.uuid4().hex
                session["user_id"] = user_id

            current_advisor = session.get(
                "advisor_name",
                data["advisor_name"].strip()
            )

            requested_advisor = data[
                "advisor_name"
            ].strip()

            changes = int(
                session.get("name_changes", 0)
            )

            locked = bool(
                session.get("name_locked", False)
            )

            # -------------------------------------
            # Advisor name change
            # -------------------------------------

            if requested_advisor != current_advisor:

                if locked or changes >= 3:

                    return {
                        "status": "error",
                        "message":
                            "تعداد تغییر نام مشاور به ۳ بار رسیده و نام مشاور قفل شده است.",
                        "advisor_name":
                            current_advisor,
                        "name_changes":
                            changes,
                        "name_changes_remaining":
                            0,
                        "name_locked":
                            True
                    }

                changes += 1
                current_advisor = requested_advisor

                if changes >= 3:
                    locked = True

            session["advisor_name"] = current_advisor
            session["name_changes"] = changes
            session["name_locked"] = locked

            data["advisor_name"] = current_advisor

        # -----------------------------------------
        # Save profile on server
        # -----------------------------------------

        save_profile_file(
            user_id,
            data
        )

        response = JSONResponse({
            "status": "ok",
            "user_id": user_id,
            "profile": data,
            "advisor_name":
                session["advisor_name"],
            "name_changes":
                session["name_changes"],
            "name_changes_remaining":
                max(
                    0,
                    3 - session["name_changes"]
                ),
            "name_locked":
                session["name_locked"],
            "profile_image":
                avatar_url(user_id),
            "natal":
                natal_chart
        })

        set_session(
            response,
            session,
            request
        )

        return response

    except Exception as exc:

        return JSONResponse(
            {
                "status": "error",
                "message": str(exc),
                "trace": traceback.format_exc()
            },
            status_code=400
        )


# =========================================================
# UPLOAD AVATAR
# =========================================================

@app.post("/profile/photo")
async def upload_photo(
    request: Request,
    image: UploadFile = File(...)
):

    session = get_session(request)

    if not session:
        return JSONResponse(
            {
                "status": "error",
                "message":
                    "ابتدا پروفایل خود را ذخیره کنید."
            },
            status_code=401
        )

    user_id = session.get("user_id")

    if not user_id:
        return JSONResponse(
            {
                "status": "error",
                "message":
                    "شناسه کاربر پیدا نشد."
            },
            status_code=401
        )

    try:

        await optimize_avatar(
            image,
            user_id
        )

        response = JSONResponse({
            "status": "ok",
            "profile_image":
                avatar_url(user_id)
        })

        set_session(
            response,
            session,
            request
        )

        return response

    except Exception as exc:

        return JSONResponse(
            {
                "status": "error",
                "message": str(exc)
            },
            status_code=400
        )


# =========================================================
# SERVE AVATAR
# =========================================================

@app.get("/profile/avatar/{user_id}.jpg")
async def get_avatar(
    user_id: str,
    request: Request
):

    session = get_session(request)

    if not session:
        return JSONResponse(
            {
                "status": "error",
                "message": "دسترسی مجاز نیست."
            },
            status_code=403
        )

    if session.get("user_id") != user_id:
        return JSONResponse(
            {
                "status": "error",
                "message": "دسترسی مجاز نیست."
            },
            status_code=403
        )

    path = avatar_path(user_id)

    if not path.exists():
        return JSONResponse(
            {
                "status": "error",
                "message": "عکس پیدا نشد."
            },
            status_code=404
        )

    from fastapi.responses import FileResponse

    return FileResponse(
        path,
        media_type="image/jpeg",
        headers={
            "Cache-Control":
                "private, max-age=3600"
        }
    )


# =========================================================
# DELETE AVATAR
# =========================================================

@app.delete("/profile/photo")
async def delete_photo(request: Request):

    session = get_session(request)

    if not session:
        return {
            "status": "error",
            "message": "پروفایل فعال نیست."
        }

    user_id = session.get("user_id")

    if not user_id:
        return {
            "status": "error",
            "message": "شناسه کاربر پیدا نشد."
        }

    delete_avatar(user_id)

    response = JSONResponse({
        "status": "ok",
        "profile_image": None
    })

    set_session(
        response,
        session,
        request
    )

    return response


# =========================================================
# NATAL
# =========================================================

@app.get("/natal")
async def natal_get(request: Request):

    session = get_session(request)

    if not session:
        return {
            "status": "error",
            "message":
                "ابتدا پروفایل خود را ذخیره کنید."
        }

    profile = load_profile(
        session["user_id"]
    )

    if not profile:
        return {
            "status": "error",
            "message":
                "پروفایل پیدا نشد."
        }

    try:
        return natal.get_natal_chart(profile)

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
            "trace": traceback.format_exc()
        }


@app.post("/natal")
async def natal_post(profile: Profile):

    try:
        return natal.get_natal_chart(
            profile.model_dump()
        )

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
            "trace": traceback.format_exc()
        }


# =========================================================
# TRANSITS / ANALYSIS
# =========================================================

@app.get("/analysis")
async def analysis_get(request: Request):

    session = get_session(request)

    if not session:
        return {
            "status": "error",
            "message":
                "ابتدا پروفایل خود را ذخیره کنید."
        }

    profile = load_profile(
        session["user_id"]
    )

    if not profile:
        return {
            "status": "error",
            "message":
                "پروفایل پیدا نشد."
        }

    try:

        natal_chart = natal.get_natal_chart(
            profile
        )

        transit_data = (
            ephemeris.get_full_transit_analysis(
                natal_chart
            )
        )

        return {
            "status": "ok",
            "natal": natal_chart,
            "transits": transit_data
        }

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
            "trace": traceback.format_exc()
        }


@app.post("/analysis")
async def analysis_post(profile: Profile):

    try:

        data = profile.model_dump()

        natal_chart = natal.get_natal_chart(
            data
        )

        transit_data = (
            ephemeris.get_full_transit_analysis(
                natal_chart
            )
        )

        return {
            "status": "ok",
            "natal": natal_chart,
            "transits": transit_data
        }

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
            "trace": traceback.format_exc()
        }


@app.get("/transits")
async def transits():

    try:
        return ephemeris.get_today_transits()

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
            "trace": traceback.format_exc()
        }


# =========================================================
# AI ADVISOR
# =========================================================

@app.post("/advisor")
async def advisor_endpoint(
    data: dict,
    request: Request
):

    try:

        question = str(
            data.get("question", "")
        ).strip()

        history = data.get(
            "history",
            []
        )

        if not question:
            return {
                "status": "error",
                "message":
                    "لطفاً سؤال خود را وارد کنید."
            }

        session = get_session(request)

        if not session:
            return {
                "status": "error",
                "message":
                    "ابتدا پروفایل خود را ذخیره کنید."
            }

        user_id = session.get("user_id")

        profile = load_profile(
            user_id
        )

        if not profile:
            return {
                "status": "error",
                "message":
                    "پروفایل شما پیدا نشد."
            }

        # نام واقعی فعلی مشاور از Session
        profile["advisor_name"] = session.get(
            "advisor_name",
            profile.get("advisor_name", "مشاور")
        )

        result = advisor.get_advice(
            question=question,
            history=history,
            profile=profile
        )

        return result

    except Exception as exc:

        print(
            "ADVISOR ERROR:",
            repr(exc)
        )

        return {
            "status": "error",
            "message":
                "خطا در ارتباط با مشاور هوشمند.",
            "debug":
                str(exc),
            "trace":
                traceback.format_exc()
        }
'''
