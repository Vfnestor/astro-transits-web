import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from advisor import get_advice
import natal
import ephemeris


# =========================================================
# App
# =========================================================

app = FastAPI(
    title="مشاور نجومی",
    version="4.0.2",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

ROOT_INDEX = BASE_DIR / "index.html"
STATIC_DIR = BASE_DIR / "static"
STATIC_INDEX = STATIC_DIR / "index.html"

DATA_DIR = Path(
    os.getenv(
        "PROFILE_STORAGE_DIR",
        str(BASE_DIR / "data" / "astro_profiles")
    )
)

PHOTOS_DIR = DATA_DIR / "photos"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Session
# =========================================================

SESSION_COOKIE = "astro_session"

SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "change-this-secret-in-render"
)


def _sign(value: str) -> str:
    digest = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{value}.{digest}"


def _verify_signed(value: str) -> Optional[str]:
    if not value or "." not in value:
        return None

    raw, signature = value.rsplit(".", 1)

    expected = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return None

    return raw


def _get_or_create_user_id(request: Request, response: JSONResponse) -> str:
    existing = _verify_signed(
        request.cookies.get(SESSION_COOKIE, "")
    )

    if existing:
        return existing

    user_id = str(uuid.uuid4())

    response.set_cookie(
        SESSION_COOKIE,
        _sign(user_id),
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=60 * 60 * 24 * 365,
    )

    return user_id


def _get_user_id(request: Request) -> str:
    existing = _verify_signed(
        request.cookies.get(SESSION_COOKIE, "")
    )

    if existing:
        return existing

    return ""


# =========================================================
# Profile helpers
# =========================================================

def _profile_path(user_id: str) -> Path:
    return DATA_DIR / f"{user_id}.json"


def _load_profile(user_id: str) -> Dict[str, Any]:
    path = _profile_path(user_id)

    if not path.exists():
        return {
            "first_name": "",
            "family_name": "",
            "advisor_name": "",
            "birth_date": "",
            "birth_time": "",
            "city": "",
            "latitude": None,
            "longitude": None,
            "utc_offset": None,
            "name_changes": 0,
            "name_locked": False,
        }

    try:
        return json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def _save_profile(user_id: str, profile: Dict[str, Any]) -> None:
    _profile_path(user_id).write_text(
        json.dumps(
            profile,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# =========================================================
# Request models
# =========================================================

class ProfileRequest(BaseModel):
    first_name: str
    family_name: str
    advisor_name: str = ""

    birth_date: str
    birth_time: str

    city: str = ""
    latitude: float
    longitude: float
    utc_offset: float


class AdvisorRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]] = []


# =========================================================
# Root
# =========================================================

@app.get("/")
async def root():
    """
    Supports both layouts:

    1. /index.html
    2. /static/index.html
    """

    if ROOT_INDEX.exists():
        return FileResponse(
            ROOT_INDEX,
            media_type="text/html",
        )

    if STATIC_INDEX.exists():
        return FileResponse(
            STATIC_INDEX,
            media_type="text/html",
        )

    raise HTTPException(
        status_code=404,
        detail="index.html not found",
    )


# =========================================================
# Static files
# =========================================================

@app.get("/index.html")
async def index_file():
    if ROOT_INDEX.exists():
        return FileResponse(
            ROOT_INDEX,
            media_type="text/html",
        )

    if STATIC_INDEX.exists():
        return FileResponse(
            STATIC_INDEX,
            media_type="text/html",
        )

    raise HTTPException(
        status_code=404,
        detail="index.html not found",
    )


@app.get("/static/{filename:path}")
async def static_file(filename: str):
    file_path = STATIC_DIR / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Static file not found",
        )

    return FileResponse(file_path)


# =========================================================
# Profile
# =========================================================

@app.get("/profile/me")
async def get_profile(request: Request):
    user_id = _get_user_id(request)

    if not user_id:
        response = JSONResponse(
            {
                "authenticated": False,
                "profile": None,
            }
        )

        user_id = _get_or_create_user_id(
            request,
            response,
        )

        profile = _load_profile(user_id)

        response = JSONResponse(
            {
                "authenticated": True,
                "user_id": user_id,
                "profile": profile,
            }
        )

        response.set_cookie(
            SESSION_COOKIE,
            _sign(user_id),
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=60 * 60 * 24 * 365,
        )

        return response

    return {
        "authenticated": True,
        "user_id": user_id,
        "profile": _load_profile(user_id),
    }


@app.post("/profile")
async def save_profile(
    request: Request,
    data: ProfileRequest,
):
    user_id = _get_user_id(request)

    response = JSONResponse(
        {"status": "ok"}
    )

    if not user_id:
        user_id = _get_or_create_user_id(
            request,
            response,
        )

    old = _load_profile(user_id)

    old_advisor_name = str(
        old.get("advisor_name", "")
    ).strip()

    new_advisor_name = str(
        data.advisor_name or ""
    ).strip()

    name_changes = int(
        old.get("name_changes", 0)
    )

    name_locked = bool(
        old.get("name_locked", False)
    )

    if old_advisor_name != new_advisor_name:
        if name_locked:
            raise HTTPException(
                status_code=400,
                detail="نام مشاور برای این پروفایل قفل شده است.",
            )

        name_changes += 1

        if name_changes >= 3:
            name_locked = True

    profile = {
        "first_name": data.first_name.strip(),
        "family_name": data.family_name.strip(),
        "advisor_name": new_advisor_name,
        "birth_date": data.birth_date,
        "birth_time": data.birth_time,
        "city": data.city.strip(),
        "latitude": data.latitude,
        "longitude": data.longitude,
        "utc_offset": data.utc_offset,
        "name_changes": name_changes,
        "name_locked": name_locked,
    }

    _save_profile(
        user_id,
        profile,
    )

    response = JSONResponse(
        {
            "status": "ok",
            "user_id": user_id,
            "profile": profile,
        }
    )

    response.set_cookie(
        SESSION_COOKIE,
        _sign(user_id),
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=60 * 60 * 24 * 365,
    )

    return response


# =========================================================
# Profile photo
# =========================================================

@app.post("/profile/photo")
async def upload_profile_photo(
    request: Request,
    file: UploadFile = File(...),
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Profile session not found.",
        )

    if not file.content_type or not file.content_type.startswith(
        "image/"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed.",
        )

    raw = await file.read()

    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image is too large. Maximum size is 8 MB.",
        )

    try:
        from PIL import Image
        from io import BytesIO

        image = Image.open(
            BytesIO(raw)
        ).convert("RGB")

        width, height = image.size
        side = min(width, height)

        left = (width - side) // 2
        top = (height - side) // 2
        right = left + side
        bottom = top + side

        image = image.crop(
            (left, top, right, bottom)
        )

        image.thumbnail(
            (320, 320)
        )

        output_path = PHOTOS_DIR / f"{user_id}.jpg"

        image.save(
            output_path,
            "JPEG",
            quality=86,
            optimize=True,
        )

        return {
            "status": "ok",
            "photo_url": f"/profile/photo/{user_id}.jpg",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process image: {exc}",
        )


@app.get("/profile/photo/{user_id}.jpg")
async def get_profile_photo(
    user_id: str,
):
    photo_path = PHOTOS_DIR / f"{user_id}.jpg"

    if not photo_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Photo not found.",
        )

    return FileResponse(
        photo_path,
        media_type="image/jpeg",
    )


@app.delete("/profile/photo")
async def delete_profile_photo(
    request: Request,
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Profile session not found.",
        )

    photo_path = PHOTOS_DIR / f"{user_id}.jpg"

    if photo_path.exists():
        photo_path.unlink()

    return {
        "status": "ok"
    }


# =========================================================
# Natal chart
# =========================================================

@app.get("/natal")
async def natal_endpoint(
    request: Request,
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Profile is not configured.",
        )

    profile = _load_profile(user_id)

    required = [
        "first_name",
        "family_name",
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "utc_offset",
    ]

    missing = [
        field
        for field in required
        if profile.get(field) in (
            None,
            "",
        )
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Birth profile is incomplete.",
                "missing": missing,
            },
        )

    try:
        chart = natal.get_natal_chart(
            profile
        )

        return chart

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Natal chart calculation failed: {exc}",
        )


# =========================================================
# Analysis
# =========================================================

@app.get("/analysis")
async def analysis_endpoint(
    request: Request,
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Profile is not configured.",
        )

    profile = _load_profile(user_id)

    try:
        chart = natal.get_natal_chart(
            profile
        )

        return {
            "status": "ok",
            "profile": profile,
            "chart": chart,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {exc}",
        )


# =========================================================
# Transits
# =========================================================

@app.get("/transits")
async def transits_endpoint(
    request: Request,
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Profile is not configured.",
        )

    profile = _load_profile(user_id)

    required = [
        "first_name",
        "family_name",
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "utc_offset",
    ]

    missing = [
        field
        for field in required
        if profile.get(field) in (
            None,
            "",
        )
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Birth profile is incomplete.",
                "missing": missing,
            },
        )

    try:
        chart = natal.get_natal_chart(
            profile
        )

        return ephemeris.get_full_transit_analysis(
            natal_chart=chart
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Transit calculation failed: {exc}",
        )

# =========================================================
# Advisor
# =========================================================

@app.post("/advisor")
async def advisor_endpoint(
    request: Request,
    data: AdvisorRequest,
):
    user_id = _get_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=400,
            detail="Profile is not configured.",
        )

    profile = _load_profile(user_id)

    required = [
        "first_name",
        "family_name",
        "birth_date",
        "birth_time",
        "latitude",
        "longitude",
        "utc_offset",
    ]

    missing = [
        field
        for field in required
        if profile.get(field) in (
            None,
            "",
        )
    ]

    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Please complete your birth profile first.",
                "missing": missing,
            },
        )

    if not data.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = get_advice(
            question=data.question.strip(),
            history=data.history,
            profile=profile,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Advisor error: {exc}",
        )


# =========================================================
# Health
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "astro-transits",
        "version": "4.0.2",
        "openai_configured": bool(
            os.getenv("OPENAI_API_KEY")
        ),
        "profile_storage": str(
            DATA_DIR
        ),
        "photo_storage": str(
            PHOTOS_DIR
        ),
        "index_root_exists": ROOT_INDEX.exists(),
        "index_static_exists": STATIC_INDEX.exists(),
    }


# =========================================================
# Debug
# =========================================================

@app.get("/debug")
async def debug():
    return {
        "base_dir": str(BASE_DIR),
        "root_index": str(ROOT_INDEX),
        "root_index_exists": ROOT_INDEX.exists(),
        "static_dir": str(STATIC_DIR),
        "static_index": str(STATIC_INDEX),
        "static_index_exists": STATIC_INDEX.exists(),
        "data_dir": str(DATA_DIR),
        "photos_dir": str(PHOTOS_DIR),
        "openai_configured": bool(
            os.getenv("OPENAI_API_KEY")
        ),
    }
