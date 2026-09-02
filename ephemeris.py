import swisseph as swe
from datetime import datetime

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

ASPECTS = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

ORB = 3.0  # درجهٔ مجاز اختلاف برای تشخیص آسپکت


def _to_julian_day(dt: datetime):
    h = dt.hour + dt.minute / 60.0
    return swe.julday(dt.year, dt.month, dt.day, h, swe.GREG_CAL)


def _deg_diff(a: float, b: float):
    diff = abs(a - b) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def get_today_transits():
    now = datetime.utcnow()
    jd = _to_julian_day(now)

    positions = {}
    for name, code in PLANETS.items():
        result = swe.calc(jd, code)
        lon = result[0]   # فقط درجه
        positions[name] = lon

    transits = []
    names = list(positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            diff = _deg_diff(positions[p1], positions[p2])
            for aspect_name, aspect_deg in ASPECTS.items():
                if abs(diff - aspect_deg) <= ORB:
                    transits.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": aspect_name,
                        "exact_diff": diff,
                    })

    return {
        "status": "ok",
        "generated_at": now.isoformat(),
        "positions": positions,
        "transits": transits,
    }


def detect_aspects(natal_chart: dict | None):
    today = get_today_transits()
    return today.get("transits", [])
