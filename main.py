"main.py"

import os
import json
import uuid
import hmac
import hashlib
from pathlib import Path
from io import BytesIO
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image, ImageOps, UnidentifiedImageError

from natal import get_natal_chart
from ephemeris import get_full_transit_analysis
from advisor import ask_openai_advisor


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Astro Transits",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

# On Render, use a Persistent Disk if PROFILE_STORAGE_DIR is set.
# Example:
# PROFILE_STORAGE_DIR=/var/data/astro_profiles
PROFILE_STORAGE_DIR = Path(
    os.getenv(
        "PROFILE_STORAGE_DIR",
        str(BASE_DIR / "data" / "astro_profiles")
    )
)

PROFILE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_DATA_DIR = PROFILE_STORAGE_DIR / "profiles"
PHOTO_DIR = PROFILE_STORAGE_DIR / "photos"

PROFILE_DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTO_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

SESSION_COOKIE = "astro_session"

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "CHANGE_THIS_SESSION_SECRET"
)

MAX_PHOTO_SIZE = 8 * 1024 * 1024
PHOTO_SIZE = 320

ADVISOR_ROLE = "مشاور نجومی و آشنا به علم اعداد"


# ============================================================
# MODELS
# ============================================================

class Profile(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    family_name: str = Field(..., min_length=1, max_length=100)

    advisor_name: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    birth_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )

    birth_time: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}$"
    )

    city: str = Field(..., min_length=1, max_length=120)

    latitude: float = Field(..., ge=-90, le=90)

    longitude: float = Field(..., ge=-180, le=180)

    utc_offset: float = Field(..., ge=-14, le=14)


class AdvisorRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )

    history: list = Field(
        default_factory=list
    )


# ============================================================
# SESSION HELPERS
# ============================================================

def _sign_value(value: str) -> str:
    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return signature


def _encode_session(session: dict) -> str:
    raw = json.dumps(
        session,
        ensure_ascii=False,
        separators=(",", ":")
    )

    signature = _sign_value(raw)

    payload = json.dumps(
        {
            "data": raw,
            "signature": signature
        },
        ensure_ascii=False,
        separators=(",", ":")
    )

    return payload


def _decode_session(value: Optional[str]) -> Optional[dict]:
    if not value:
        return None

    try:
        payload = json.loads(value)

        raw = payload.get("data")
        signature = payload.get("signature")

        if not raw or not signature:
            return None

        expected = _sign_value(raw)

        if not hmac.compare_digest(
            signature,
            expected
        ):
            return None

        return json.loads(raw)

    except Exception:
        return None


def _new_session() -> dict:
    return {
        "user_id": str(uuid.uuid4()),
        "advisor_name": "",
        "name_changes": 0,
        "name_locked": False
    }


def _get_session(request: Request) -> Optional[dict]:
    cookie = request.cookies.get(SESSION_COOKIE)
    return _decode_session(cookie)


def _set_session_cookie(
    response,
    session: dict,
    request: Request
):
    secure = request.url.scheme == "https"

    response.set_cookie(
        key=SESSION_COOKIE,
        value=_encode_session(session),
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        secure=secure,
        samesite="lax"
    )


# ============================================================
# PROFILE STORAGE
# ============================================================

def _profile_path(user_id: str) -> Path:
    return PROFILE_DATA_DIR / f"{user_id}.json"


def _load_profile(user_id: str) -> Optional[dict]:
    path = _profile_path(user_id)

    if not path.exists():
        return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return None


def _save_profile(
    user_id: str,
    profile: dict
):
    path = _profile_path(user_id)
    temp_path = path.with_suffix(".tmp")

    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            profile,
            f,
            ensure_ascii=False,
            indent=2
        )

    temp_path.replace(path)


def _avatar_exists(user_id: str) -> bool:
    return (
        PHOTO_DIR /
        f"{user_id}.jpg"
    ).exists()


def _avatar_url(user_id: str) -> Optional[str]:
    path = PHOTO_DIR / f"{user_id}.jpg"

    if not path.exists():
        return None

    try:
        version = int(
            path.stat().st_mtime
        )
    except Exception:
        version = 1

    return (
        f"/profile/photo/"
        f"{user_id}.jpg?v={version}"
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def _clean_text(value: str) -> str:
    return " ".join(
        value.strip().split()
    )


def _normalize_profile(profile: Profile) -> Profile:
    return Profile(
        first_name=_clean_text(
            profile.first_name
        ),
        family_name=_clean_text(
            profile.family_name
        ),
        advisor_name=_clean_text(
            profile.advisor_name
        ),
        birth_date=profile.birth_date.strip(),
        birth_time=profile.birth_time.strip(),
        city=_clean_text(
            profile.city
        ),
        latitude=profile.latitude,
        longitude=profile.longitude,
        utc_offset=profile.utc_offset
    )


def _profile_response(
    profile: dict,
    session: dict,
    warning: Optional[str] = None
):
    result = {
        "status": "ok",
        "user_id": session["user_id"],
        "profile": profile,
        "advisor_name": session.get(
            "advisor_name",
            profile.get("advisor_name", "")
        ),
        "name_changes": session.get(
            "name_changes",
            0
        ),
        "name_locked": session.get(
            "name_locked",
            False
        ),
        "advisor_role": ADVISOR_ROLE,
        "avatar_url": _avatar_url(
            session["user_id"]
        )
    }

    if warning:
        result["warning"] = warning

    return result


# ============================================================
# HOME
# ============================================================

@app.get("/")
async def home():
    index_path = STATIC_DIR / "index.html"

    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail="index.html not found"
        )

    return FileResponse(
        index_path,
        media_type="text/html"
    )


# ============================================================
# PROFILE
# ============================================================

@app.get("/profile/me")
async def profile_me(request: Request):
    session = _get_session(request)

    if not session:
        return {
            "status": "empty",
            "profile": None,
            "user_id": None,
            "avatar_url": None,
            "advisor_role": ADVISOR_ROLE
        }

    user_id = session.get("user_id")

    if not user_id:
        return {
            "status": "empty",
            "profile": None,
            "user_id": None,
            "avatar_url": None,
            "advisor_role": ADVISOR_ROLE
        }

    profile = _load_profile(user_id)

    if not profile:
        return {
            "status": "empty",
            "profile": None,
            "user_id": user_id,
            "avatar_url": _avatar_url(user_id),
            "advisor_role": ADVISOR_ROLE
        }

    return _profile_response(
        profile,
        session
    )


@app.post("/profile")
async def save_profile(
    profile: Profile,
    request: Request
):
    profile = _normalize_profile(profile)

    session = _get_session(request)

    if not session:
        session = _new_session()

    user_id = session["user_id"]

    old_profile = _load_profile(
        user_id
    )

    old_advisor_name = (
        session.get("advisor_name")
        or (
            old_profile or {}
        ).get("advisor_name", "")
    )

    requested_name = profile.advisor_name

    name_change_rejected = False
    warning = None

    # --------------------------------------------------------
    # Advisor name change policy
    # --------------------------------------------------------

    if old_advisor_name:
        if (
            requested_name !=
            old_advisor_name
        ):
            if session.get(
                "name_locked",
                False
            ):
                requested_name = (
                    old_advisor_name
                )

                name_change_rejected = True

                warning = (
                    "نام مشاور قبلاً سه بار "
                    "تغییر کرده و اکنون برای همیشه "
                    "قفل شده است."
                )

            else:
                current_changes = int(
                    session.get(
                        "name_changes",
                        0
                    )
                )

                if current_changes >= 3:
                    session["name_locked"] = True

                    requested_name = (
                        old_advisor_name
                    )

                    name_change_rejected = True

                    warning = (
                        "سقف سه تغییر نام مشاور "
                        "قبلاً استفاده شده است."
                    )

                else:
                    current_changes += 1

                    session["name_changes"] = (
                        current_changes
                    )

                    if current_changes >= 3:
                        session["name_locked"] = True

    session["advisor_name"] = (
        requested_name
    )

    # Build final profile.
    profile_dict = profile.model_dump()

    profile_dict["advisor_name"] = (
        requested_name
    )

    profile_dict["updated_at"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    _save_profile(
        user_id,
        profile_dict
    )

    response = JSONResponse(
        _profile_response(
            profile_dict,
            session,
            warning
        )
    )

    response.headers[
        "X-Profile-Name-Change-Rejected"
    ] = (
        "true"
        if name_change_rejected
        else "false"
    )

    _set_session_cookie(
        response,
        session,
        request
    )

    return response


# ============================================================
# PROFILE PHOTO UPLOAD
# ============================================================

@app.post("/profile/photo")
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...)
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=401,
            detail="ابتدا پروفایل خود را ذخیره کنید."
        )

    user_id = session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="شناسه کاربر معتبر نیست."
        )

    profile = _load_profile(
        user_id
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="ابتدا اطلاعات پروفایل را ذخیره کنید."
        )

    content_type = (
        file.content_type or ""
    ).lower()

    if not content_type.startswith(
        "image/"
    ):
        raise HTTPException(
            status_code=400,
            detail="فایل انتخاب‌شده تصویر نیست."
        )

    raw = bytearray()

    while True:
        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        raw.extend(chunk)

        if len(raw) > MAX_PHOTO_SIZE:
            raise HTTPException(
                status_code=413,
                detail=(
                    "حجم عکس نباید بیشتر از "
                    "8 مگابایت باشد."
                )
            )

    if not raw:
        raise HTTPException(
            status_code=400,
            detail="فایل تصویر خالی است."
        )

    try:
        image = Image.open(
            BytesIO(raw)
        )

        image.verify()

        image = Image.open(
            BytesIO(raw)
        )

        image = ImageOps.exif_transpose(
            image
        )

        if image.mode in (
            "RGBA",
            "LA"
        ):
            background = Image.new(
                "RGB",
                image.size,
                (12, 15, 25)
            )

            alpha = image.getchannel(
                "A"
            )

            background.paste(
                image,
                mask=alpha
            )

            image = background

        else:
            image = image.convert(
                "RGB"
            )

        image = ImageOps.fit(
            image,
            (
                PHOTO_SIZE,
                PHOTO_SIZE
            ),
            method=Image.Resampling.LANCZOS,
            centering=(
                0.5,
                0.5
            )
        )

    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError
    ):
        raise HTTPException(
            status_code=400,
            detail="تصویر معتبر نیست یا قابل پردازش نیست."
        )

    output_path = (
        PHOTO_DIR /
        f"{user_id}.jpg"
    )

    try:
        image.save(
            output_path,
            format="JPEG",
            quality=86,
            optimize=True,
            progressive=True
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "ذخیره عکس انجام نشد: "
                f"{str(exc)}"
            )
        )

    return {
        "status": "ok",
        "message": "عکس پروفایل با موفقیت بهینه شد.",
        "avatar_url": _avatar_url(
            user_id
        )
    }


# ============================================================
# PROFILE PHOTO SERVE
# ============================================================

@app.get(
    "/profile/photo/{user_id}.jpg"
)
async def get_profile_photo(
    user_id: str,
    request: Request
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    current_user_id = session.get(
        "user_id"
    )

    if current_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    photo_path = (
        PHOTO_DIR /
        f"{user_id}.jpg"
    )

    if not photo_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Profile photo not found"
        )

    return FileResponse(
        photo_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control":
                "private, max-age=86400"
        }
    )


# ============================================================
# DELETE PROFILE PHOTO
# ============================================================

@app.delete("/profile/photo")
async def delete_profile_photo(
    request: Request
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    photo_path = (
        PHOTO_DIR /
        f"{user_id}.jpg"
    )

    if photo_path.exists():
        try:
            photo_path.unlink()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "حذف عکس انجام نشد: "
                    f"{str(exc)}"
                )
            )

    return {
        "status": "ok",
        "avatar_url": None
    }


# ============================================================
# NATAL CHART
# ============================================================

@app.get("/natal")
async def natal_get(
    request: Request
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=400,
            detail="پروفایل ثبت نشده است."
        )

    profile = _load_profile(
        session["user_id"]
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="ابتدا پروفایل را ذخیره کنید."
        )

    chart = get_natal_chart(
        profile
    )

    return chart


@app.post("/natal")
async def natal_post(
    profile: Profile
):
    profile = _normalize_profile(
        profile
    )

    return get_natal_chart(
        profile.model_dump()
    )


# ============================================================
# TRANSITS / ANALYSIS
# ============================================================

@app.get("/analysis")
async def analysis_get(
    request: Request
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=400,
            detail="پروفایل ثبت نشده است."
        )

    profile = _load_profile(
        session["user_id"]
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="ابتدا پروفایل را ذخیره کنید."
        )

    natal_chart = get_natal_chart(
        profile
    )

    return get_full_transit_analysis(
        natal_chart
    )


@app.post("/analysis")
async def analysis_post(
    profile: Profile
):
    profile = _normalize_profile(
        profile
    )

    profile_dict = profile.model_dump()

    natal_chart = get_natal_chart(
        profile_dict
    )

    return get_full_transit_analysis(
        natal_chart
    )


@app.get("/transits")
async def transits_get():
    return get_full_transit_analysis()


# ============================================================
# AI ADVISOR
# ============================================================

@app.post("/advisor")
async def advisor(
    request_data: AdvisorRequest,
    request: Request
):
    session = _get_session(request)

    if not session:
        raise HTTPException(
            status_code=400,
            detail="ابتدا پروفایل خود را ثبت کنید."
        )

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="شناسه کاربر معتبر نیست."
        )

    profile = _load_profile(
        user_id
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail="ابتدا پروفایل خود را ذخیره کنید."
        )

    natal_chart = get_natal_chart(
        profile
    )

    transit_data = get_full_transit_analysis(
        natal_chart
    )

    advisor_name = session.get(
        "advisor_name"
    ) or profile.get(
        "advisor_name",
        ""
    )

    try:
        result = ask_openai_advisor(
            question=request_data.question,
            profile=profile,
            natal_chart=natal_chart,
            transit_data=transit_data,
            history=request_data.history,
            advisor_name=advisor_name
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "خطا در ارتباط با مشاور هوش مصنوعی: "
                f"{str(exc)}"
            )
        )

    return {
        "status": "ok",
        "answer": result.get(
            "answer",
            ""
        ),
        "advisor_name": advisor_name,
        "advisor_role": ADVISOR_ROLE,
        "model": result.get(
            "model"
        ),
        "numerology": natal_chart.get(
            "numerology",
            {}
        )
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():
    openai_configured = bool(
        os.getenv("OPENAI_API_KEY")
    )

    return {
        "status": "ok",
        "service": "astro-transits",
        "version": "4.0.0",
        "openai_configured": openai_configured,
        "profile_storage": str(
            PROFILE_STORAGE_DIR
        ),
        "photo_storage": str(
            PHOTO_DIR
        )
    }


# ============================================================
# DEBUG
# ============================================================

@app.get("/debug")
async def debug():
    return {
        "status": "ok",
        "python": os.sys.version,
        "base_dir": str(
            BASE_DIR
        ),
        "static_dir": str(
            STATIC_DIR
        ),
        "profile_storage": str(
            PROFILE_STORAGE_DIR
        ),
        "photo_dir": str(
            PHOTO_DIR
        ),
        "openai_configured": bool(
            os.getenv("OPENAI_API_KEY")
        ),
        "openai_model": os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna"
        )
    }
