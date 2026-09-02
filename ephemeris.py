from datetime import datetime, timezone
from pathlib import Path

import swisseph as swe


# =========================================================
# ASTRO VAHID — EPHEMERIS ENGINE
# Version 3.0
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
EPHE_PATH = BASE_DIR / "ephe"

swe.set_ephe_path(str(EPHE_PATH))


# =========================================================
# PLANETS
# =========================================================

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


PLANET_FA = {
    "Sun": "خورشید",
    "Moon": "ماه",
    "Mercury": "عطارد",
    "Venus": "زهره",
    "Mars": "مریخ",
    "Jupiter": "مشتری",
    "Saturn": "زحل",
    "Uranus": "اورانوس",
    "Neptune": "نپتون",
    "Pluto": "پلوتو",
    "North Node": "گره شمالی",
    "South Node": "گره جنوبی",
    "ASC": "طالع",
    "MC": "وسط آسمان",
}


PLANET_SYMBOL = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "North Node": "☊",
    "South Node": "☋",
    "ASC": "ASC",
    "MC": "MC",
}


# =========================================================
# ASPECTS
# =========================================================

ASPECTS = {
    "conjunction": {
        "degree": 0,
        "orb": 8.0,
        "fa": "هم‌نشینی",
        "symbol": "☌",
        "weight": 5,
    },
    "sextile": {
        "degree": 60,
        "orb": 5.0,
        "fa": "تسدیس",
        "symbol": "⚹",
        "weight": 3,
    },
    "square": {
        "degree": 90,
        "orb": 7.0,
        "fa": "تربیع",
        "symbol": "□",
        "weight": 4,
    },
    "trine": {
        "degree": 120,
        "orb": 7.0,
        "fa": "تثلیث",
        "symbol": "△",
        "weight": 4,
    },
    "opposition": {
        "degree": 180,
        "orb": 8.0,
        "fa": "مقابله",
        "symbol": "☍",
        "weight": 5,
    },
    "quincunx": {
        "degree": 150,
        "orb": 3.0,
        "fa": "کوینکانکس",
        "symbol": "⚻",
        "weight": 2,
    },
}


# =========================================================
# HELPERS
# =========================================================

def _to_julian_day(dt: datetime) -> float:
    """
    Convert datetime to Julian Day.

    Swiss Ephemeris works with UTC.
    """

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    hour = (
        dt.hour
        + dt.minute / 60.0
        + dt.second / 3600.0
        + dt.microsecond / 3600000000.0
    )

    return swe.julday(
        dt.year,
        dt.month,
        dt.day,
        hour,
        swe.GREG_CAL,
    )


def _degree_difference(a: float, b: float) -> float:
    """
    Smallest angular distance between two longitudes.
    """

    diff = abs(a - b) % 360.0

    if diff > 180.0:
        diff = 360.0 - diff

    return diff


def _normalize_degree(value: float) -> float:
    return value % 360.0


def _find_aspect(diff: float):
    """
    Find the strongest applicable aspect.
    """

    candidates = []

    for name, data in ASPECTS.items():
        aspect_degree = data["degree"]
        orb_limit = data["orb"]

        orb = abs(diff - aspect_degree)

        if orb <= orb_limit:
            candidates.append(
                (
                    orb,
                    name,
                    aspect_degree,
                    data,
                )
            )

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])

    orb, name, aspect_degree, data = candidates[0]

    return {
        "aspect": name,
        "aspect_fa": data["fa"],
        "aspect_symbol": data["symbol"],
        "aspect_degree": aspect_degree,
        "orb": round(orb, 4),
        "weight": data["weight"],
    }


def _format_position(longitude: float) -> dict:
    """
    Convert absolute longitude into zodiac sign + degree.
    """

    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    signs_fa = [
        "حمل",
        "ثور",
        "جوزا",
        "سرطان",
        "اسد",
        "سنبله",
        "میزان",
        "عقرب",
        "قوس",
        "جدی",
        "دلو",
        "حوت",
    ]

    longitude = _normalize_degree(longitude)

    sign_index = int(longitude // 30)
    degree_float = longitude % 30

    degree = int(degree_float)
    minutes_float = (degree_float - degree) * 60

    minute = int(minutes_float)
    seconds = round((minutes_float - minute) * 60, 1)

    return {
        "longitude": round(longitude, 6),
        "sign": signs[sign_index],
        "sign_fa": signs_fa[sign_index],
        "degree": degree,
        "minute": minute,
        "second": seconds,
        "formatted": (
            f"{degree}° {minute:02d}′ "
            f"{seconds:04.1f}″ {signs_fa[sign_index]}"
        ),
    }


# =========================================================
# PLANET POSITIONS
# =========================================================

def _calculate_positions(jd: float) -> dict:
    positions = {}

    for name, code in PLANETS.items():

        result = swe.calc(
            jd,
            code,
        )

        longitude = result[0][0]

        speed_longitude = result[0][3]

        position = _format_position(longitude)

        positions[name] = {
            "longitude": position["longitude"],
            "sign": position["sign"],
            "sign_fa": position["sign_fa"],
            "degree": position["degree"],
            "minute": position["minute"],
            "second": position["second"],
            "formatted": position["formatted"],
            "retrograde": speed_longitude < 0,
            "speed": round(speed_longitude, 6),
            "planet_fa": PLANET_FA[name],
            "symbol": PLANET_SYMBOL[name],
        }

    return positions


# =========================================================
# TRANSIT → TRANSIT ASPECTS
# =========================================================

def _calculate_transit_aspects(positions: dict) -> list:
    results = []

    names = list(positions.keys())

    for i in range(len(names)):

        for j in range(i + 1, len(names)):

            p1 = names[i]
            p2 = names[j]

            lon1 = positions[p1]["longitude"]
            lon2 = positions[p2]["longitude"]

            diff = _degree_difference(
                lon1,
                lon2,
            )

            aspect = _find_aspect(diff)

            if not aspect:
                continue

            results.append(
                {
                    "planet1": p1,
                    "planet1_fa": PLANET_FA[p1],
                    "planet1_symbol": PLANET_SYMBOL[p1],

                    "planet2": p2,
                    "planet2_fa": PLANET_FA[p2],
                    "planet2_symbol": PLANET_SYMBOL[p2],

                    "aspect": aspect["aspect"],
                    "aspect_fa": aspect["aspect_fa"],
                    "aspect_symbol": aspect["aspect_symbol"],

                    "exact_diff": round(diff, 4),
                    "orb": aspect["orb"],
                    "weight": aspect["weight"],
                }
            )

    results.sort(
        key=lambda x: (
            -x["weight"],
            x["orb"],
        )
    )

    return results


# =========================================================
# NATAL TARGET EXTRACTION
# =========================================================

def _extract_natal_targets(natal_chart: dict) -> dict:
    """
    Extract natal planets, nodes and angles from natal.py output.
    """

    targets = {}

    planets = natal_chart.get("planets", {})

    for name, data in planets.items():

        if "longitude" not in data:
            continue

        targets[name] = {
            "longitude": float(data["longitude"]),
            "target_type": "planet",
            "house": data.get("house"),
            "sign": data.get("sign"),
            "sign_fa": data.get("sign_fa"),
        }

    nodes = natal_chart.get("nodes", {})

    for name, data in nodes.items():

        if "longitude" not in data:
            continue

        targets[name] = {
            "longitude": float(data["longitude"]),
            "target_type": "node",
            "house": data.get("house"),
            "sign": data.get("sign"),
            "sign_fa": data.get("sign_fa"),
        }

    angles = natal_chart.get("angles", {})

    if "ascendant" in angles:

        asc = angles["ascendant"]

        if isinstance(asc, dict):
            asc_lon = asc.get("longitude")
        else:
            asc_lon = asc

        if asc_lon is not None:

            targets["ASC"] = {
                "longitude": float(asc_lon),
                "target_type": "angle",
                "house": 1,
            }

    if "mc" in angles:

        mc = angles["mc"]

        if isinstance(mc, dict):
            mc_lon = mc.get("longitude")
        else:
            mc_lon = mc

        if mc_lon is not None:

            targets["MC"] = {
                "longitude": float(mc_lon),
                "target_type": "angle",
                "house": 10,
            }

    return targets


# =========================================================
# TRANSIT → NATAL
# =========================================================

def _calculate_natal_transits(
    transit_positions: dict,
    natal_chart: dict,
) -> list:

    natal_targets = _extract_natal_targets(
        natal_chart
    )

    results = []

    for transit_name, transit_data in transit_positions.items():

        transit_lon = transit_data["longitude"]

        for natal_name, natal_data in natal_targets.items():

            natal_lon = natal_data["longitude"]

            diff = _degree_difference(
                transit_lon,
                natal_lon,
            )

            aspect = _find_aspect(diff)

            if not aspect:
                continue

            importance = aspect["weight"]

            # Personal planets and angles receive more weight.
            if natal_name in {
                "Sun",
                "Moon",
                "ASC",
                "MC",
            }:
                importance += 2

            if transit_name in {
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
                "Jupiter",
            }:
                importance += 1

            results.append(
                {
                    "transit_planet": transit_name,
                    "transit_planet_fa": PLANET_FA[transit_name],
                    "transit_symbol": PLANET_SYMBOL[transit_name],

                    "natal_target": natal_name,
                    "natal_target_fa": PLANET_FA.get(
                        natal_name,
                        natal_name,
                    ),
                    "natal_symbol": PLANET_SYMBOL.get(
                        natal_name,
                        "",
                    ),

                    "target_type": natal_data["target_type"],

                    "aspect": aspect["aspect"],
                    "aspect_fa": aspect["aspect_fa"],
                    "aspect_symbol": aspect["aspect_symbol"],

                    "exact_diff": round(diff, 4),
                    "orb": aspect["orb"],

                    "importance": importance,

                    "transit_position": transit_data["formatted"],

                    "natal_sign": natal_data.get("sign"),
                    "natal_sign_fa": natal_data.get("sign_fa"),

                    "natal_house": natal_data.get("house"),

                    "transit_retrograde": transit_data.get(
                        "retrograde",
                        False,
                    ),
                }
            )

    # Most important first.
    results.sort(
        key=lambda x: (
            -x["importance"],
            x["orb"],
        )
    )

    return results


# =========================================================
# INTERPRETATION
# =========================================================

def _interpret_natal_transit(item: dict) -> str:

    transit = item["transit_planet_fa"]
    natal = item["natal_target_fa"]
    aspect = item["aspect_fa"]

    if item["aspect"] == "trine":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ این الگو معمولاً نماد جریان هماهنگ‌تر "
            f"و امکان استفاده راحت‌تر از انرژی این دو نقطه است."
        )

    if item["aspect"] == "sextile":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ می‌تواند یک فرصت قابل استفاده ایجاد کند، "
            f"به‌خصوص اگر آگاهانه برای آن اقدام شود."
        )

    if item["aspect"] == "square":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ این الگو بیشتر به فشار، اصطکاک یا نیاز "
            f"به تغییر و سازگاری اشاره می‌کند."
        )

    if item["aspect"] == "opposition":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ ممکن است یک محور دوگانه یا کشمکش "
            f"بین دو حوزه زندگی را برجسته کند."
        )

    if item["aspect"] == "conjunction":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ این موضوع می‌تواند این بخش از چارت "
            f"را به یکی از نقاط برجسته دوره فعلی تبدیل کند."
        )

    if item["aspect"] == "quincunx":

        return (
            f"ترانزیت {transit} با {natal} در حالت {aspect} "
            f"قرار دارد؛ معمولاً نیازمند تنظیم، اصلاح یا "
            f"تغییر زاویه نگاه است."
        )

    return (
        f"ترانزیت {transit} و {natal} "
        f"نیازمند توجه بیشتر است."
    )


# =========================================================
# MAIN TRANSIT FUNCTION
# =========================================================

def get_today_transits():

    now = datetime.now(
        timezone.utc
    )

    jd = _to_julian_day(
        now
    )

    positions = _calculate_positions(
        jd
    )

    transit_aspects = _calculate_transit_aspects(
        positions
    )

    # -----------------------------------------------------
    # Load natal chart lazily.
    # This avoids circular imports.
    # -----------------------------------------------------

    natal_transits = []

    try:

        import natal

        natal_chart = natal.get_natal_chart()

        natal_transits = _calculate_natal_transits(
            positions,
            natal_chart,
        )

        for item in natal_transits:
            item["interpretation"] = (
                _interpret_natal_transit(item)
            )

    except Exception as exc:

        natal_transits = []

        print(
            "Natal transit calculation error:",
            repr(exc),
        )

    return {
        "status": "ok",

        "generated_at": now.isoformat(),

        "ephemeris_path": str(
            EPHE_PATH
        ),

        "positions": positions,

        "transits": transit_aspects,

        "natal_transits": natal_transits,

        "summary": {
            "planet_count": len(
                positions
            ),

            "transit_aspect_count": len(
                transit_aspects
            ),

            "natal_transit_count": len(
                natal_transits
            ),

            "important_natal_transits": len(
                [
                    x
                    for x in natal_transits
                    if x["importance"] >= 6
                ]
            ),
        },
    }


# =========================================================
# COMPATIBILITY FUNCTION FOR ADVISOR
# =========================================================

def detect_aspects(
    natal_chart: dict | None = None
):

    data = get_today_transits()

    if natal_chart is not None:

        return _calculate_natal_transits(
            data["positions"],
            natal_chart,
        )

    return data.get(
        "natal_transits",
        []
    )
