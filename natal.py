latisseph as swe
from datetime import datetime

# فولدر ephe باید کنار main.py باشد و سه فایل:
# sepl_18.se1, semo_18.se1, seas_18.se1 داخلش باشند.
swe.set_ephe_path("ephe")

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# نمونهٔ تولد؛ بعداً می‌تونی از فرم فرانت‌اند بگیری
BIRTH_DATE = (1990, 3, 21)   # سال، ماه، روز
BIRTH_TIME = (12, 0)         # ساعت، دقیقه
BIRTH_LAT = 35.6892          # تهران
BIRTH_LON = 51.3890


def _to_julian_day(year, month, day, hour, minute):
    h = hour + minute / 60.0
    return swe.julday(year, month, day, h, swe.GREG_CAL)


def _deg_to_sign(deg: float):
    sign_index = int(deg // 30)
    return SIGNS[sign_index], deg % 30


def get_natal_chart():
    jd = _to_julian_day(
        BIRTH_DATE[0], BIRTH_DATE[1], BIRTH_DATE[2],
        BIRTH_TIME[0], BIRTH_TIME[1]
    )

    chart = {}
    for name, code in PLANETS.items():
        result = swe.calc(jd, code)
        lon = result[0]
        lat = result[1]
        sign, pos_in_sign = _deg_to_sign(lon)

        chart[name] = {
            "longitude": lon,
            "latitude": lat,
            "sign": sign,
            "degree_in_sign": pos_in_sign,
        }

    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "location": {
            "lat": BIRTH_LAT,
            "lon": BIRTH_LON,
        },
        "chart": chart,
    }
