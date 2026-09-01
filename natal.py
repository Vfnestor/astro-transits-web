import swisseph as swe
from datetime import datetime
swe.setephepath("ephe")
# تنظیم مسیر دیتابیس سیارات (در آینده می‌تونی فایل‌های ephemeris رو روی Render بذاری)
# swe.set_ephe_path('/opt/render/project/src/ephe')  # فعلاً کامنت

# نمونهٔ دادهٔ تولد؛ بعداً می‌تونی از فرم فرانت‌اند بگیری
BIRTH_DATE = (1990, 3, 21)   # سال، ماه، روز
BIRTH_TIME = (12, 0)         # ساعت، دقیقه
BIRTH_LAT = 35.6892          # تهران
BIRTH_LON = 51.3890

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def _to_julian_day(year, month, day, hour, minute):
    h = hour + minute / 60.0
    return swe.julday(year, month, day, h, swe.GREG_CAL)


def _deg_to_sign(deg):
    sign_index = int(deg // 30)
    return SIGNS[sign_index], deg % 30


def get_natal_chart():
    jd = _to_julian_day(
        BIRTH_DATE[0], BIRTH_DATE[1], BIRTH_DATE[2],
        BIRTH_TIME[0], BIRTH_TIME[1]
    )

    chart = {}
    for name, code in PLANETS.items():
        lon, lat, dist, speed_lon = swe.calc(jd, code)
        sign, pos_in_sign = _deg_to_sign(lon)
        chart[name] = {
            "longitude": lon,
            "sign": sign,
            "degree_in_sign": pos_in_sign
        }

    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "location": {
            "lat": BIRTH_LAT,
            "lon": BIRTH_LON
        },
        "chart": chart
    }
