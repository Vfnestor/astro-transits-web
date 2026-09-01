from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# اجازه دسترسی فرانت‌اند (فعلاً باز، بعداً می‌تونیم محدودش کنیم)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- چارت تولد وحید (فعلاً هاردکد، بعداً دیتابیس می‌کنیم) ---

natal_chart = {
    "asc": "Libra 22°",
    "houses": {
        1: "Libra 22° - Scorpio 20°",
        2: "Scorpio 20° - Sagittarius ...",
        # بقیه خانه‌ها را بعداً کامل می‌کنیم
    },
    "planets": {
        "Sun": {"sign": "Leo", "house": 10},
        "Moon": {"sign": "Aries", "house": 9},
        "Mars": {"sign": "Leo", "house": 10},
        "Venus": {"sign": "Aquarius", "house": 4},
        "Mercury": {"sign": "Aquarius", "house": 4},
        "Jupiter": {"sign": "Scorpio", "house": 2},
        "Saturn": {"sign": "Sagittarius", "house": 3},
        "Uranus": {"sign": "Capricorn", "house": 4},
        "Neptune": {"sign": "Capricorn", "house": 4},
        "Pluto": {"sign": "Scorpio", "house": 1},
    },
}


@app.get("/")
def root():
    return {
        "message": "نسخه 0.1 سرویس ترانزیت نجومی فعال است.",
        "now": datetime.now().isoformat(),
    }


@app.get("/natal")
def get_natal_chart():
    return {
        "message": "چارت تولد ثبت‌شده (فعلاً هاردکد).",
        "natal_chart": natal_chart,
    }


@app.get("/transits/now")
def get_transits_now():
    # نسخه 0.1: فعلاً فقط زمان فعلی را برمی‌گردانیم
    # در نسخه‌های بعدی اینجا اپهمریس و محاسبه موقعیت سیارات اضافه می‌شود
    now = datetime.now().isoformat()
    return {
        "message": "این فقط پاسخ تست نسخه 0.1 است. در نسخه بعدی، موقعیت سیارات اضافه می‌شود.",
        "now": now,
        "natal_chart_used": True,
}
