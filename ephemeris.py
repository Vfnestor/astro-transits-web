import swisseph as swe

from datetime import datetime, timezone

import natal


# =========================================================
# Swiss Ephemeris
# =========================================================

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent

swe.set_ephe_path(
    str(BASE_DIR / "ephe")
)


# =========================================================
# سیارات ترانزیتی
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


PLANET_NAMES_FA = natal.PLANET_NAMES_FA
PLANET_SYMBOLS = natal.PLANET_SYMBOLS


# =========================================================
# Aspects
# =========================================================

ASPECTS = {
    "conjunction": {
        "angle": 0,
        "orb": 6.0,
        "name_fa": "هم‌نشینی",
    },

    "opposition": {
        "angle": 180,
        "orb": 6.0,
        "name_fa": "مقابله",
    },

    "trine": {
        "angle": 120,
        "orb": 5.0,
        "name_fa": "تثلیث",
    },

    "square": {
        "angle": 90,
        "orb": 5.0,
        "name_fa": "تربیع",
    },

    "sextile": {
        "angle": 60,
        "orb": 4.0,
        "name_fa": "تسدیس",
    },

    "quincunx": {
        "angle": 150,
        "orb": 3.0,
        "name_fa": "کوینکانکس",
    },
}


# =========================================================
# Julian Day
# =========================================================

def _to_julian_day(dt):

    hour = (
        dt.hour
        + dt.minute / 60
        + dt.second / 3600
    )

    return swe.julday(
        dt.year,
        dt.month,
        dt.day,
        hour,
        swe.GREG_CAL,
    )

# Deploy sync 2026-09-02
# =========================================================
# Degree difference
# =========================================================

def _deg_diff(a, b):

    diff = abs(
        float(a) - float(b)
    ) % 360

    if diff > 180:
        diff = 360 - diff

    return diff


# =========================================================
# Transit positions
# =========================================================

def _calculate_positions(
    jd,
):

    positions = {}

    for name, code in PLANETS.items():

        result = swe.calc(
            jd,
            code,
        )

        values = result[0]

        longitude = float(
            values[0]
        )

        latitude = float(
            values[1]
        )

        speed = float(
            values[3]
        )

        positions[name] = {
            "longitude": longitude,
            "latitude": latitude,
            "speed": speed,
            "retrograde": speed < 0,
            "name_fa": PLANET_NAMES_FA[name],
            "symbol": PLANET_SYMBOLS[name],
            **natal._format_position(
                longitude
            ),
        }

    return positions


# =========================================================
# Transit-to-transit aspects
# =========================================================

def _calculate_transit_aspects(
    positions,
):

    result = []

    names = list(
        positions.keys()
    )

    for i in range(len(names)):

        for j in range(
            i + 1,
            len(names),
        ):

            p1 = names[i]
            p2 = names[j]

            diff = _deg_diff(
                positions[p1]["longitude"],
                positions[p2]["longitude"],
            )

            for aspect_name, info in ASPECTS.items():

                orb = abs(
                    diff - info["angle"]
                )

                if orb <= info["orb"]:

                    result.append({
                        "planet1": p1,
                        "planet2": p2,

                        "planet1_fa":
                            PLANET_NAMES_FA[p1],

                        "planet2_fa":
                            PLANET_NAMES_FA[p2],

                        "aspect": aspect_name,

                        "aspect_fa":
                            info["name_fa"],

                        "angle":
                            info["angle"],

                        "exact_difference":
                            round(diff, 4),

                        "orb":
                            round(orb, 4),
                    })

                    break

    result.sort(
        key=lambda x: x["orb"]
    )

    return result


# =========================================================
# Transit-to-natal aspects
# =========================================================

def _calculate_natal_transits(
    transit_positions,
    natal_chart,
):

    result = []

    natal_bodies = {}

    natal_bodies.update(
        natal_chart["planets"]
    )

    natal_bodies.update(
        natal_chart["nodes"]
    )

    for transit_name, transit in transit_positions.items():

        transit_lon = transit[
            "longitude"
        ]

        for natal_name, natal_body in natal_bodies.items():

            natal_lon = natal_body[
                "longitude"
            ]

            diff = _deg_diff(
                transit_lon,
                natal_lon,
            )

            for aspect_name, info in ASPECTS.items():

                orb = abs(
                    diff - info["angle"]
                )

                if orb <= info["orb"]:

                    result.append({

                        "transit_planet":
                            transit_name,

                        "transit_planet_fa":
                            PLANET_NAMES_FA[
                                transit_name
                            ],

                        "natal_planet":
                            natal_name,

                        "natal_planet_fa":
                            PLANET_NAMES_FA[
                                natal_name
                            ],

                        "aspect":
                            aspect_name,

                        "aspect_fa":
                            info["name_fa"],

                        "angle":
                            info["angle"],

                        "exact_difference":
                            round(
                                diff,
                                4,
                            ),

                        "orb":
                            round(
                                orb,
                                4,
                            ),

                        "natal_house":
                            natal_body.get(
                                "house"
                            ),

                        "natal_house_name_fa":
                            natal_body.get(
                                "house_name_fa"
                            ),

                        "transit_sign":
                            transit.get(
                                "sign_fa"
                            ),

                        "transit_degree":
                            transit.get(
                                "degree_in_sign"
                            ),
                    })

                    break

    result.sort(
        key=lambda x: x["orb"]
    )

    return result


# =========================================================
# Current transits
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

    transits = _calculate_transit_aspects(
        positions
    )

    return {
        "status": "ok",

        "generated_at":
            now.isoformat(),

        "positions":
            positions,

        "transits":
            transits,
    }


# =========================================================
# Full analysis
# =========================================================

def get_full_transit_analysis():

    now = datetime.now(
        timezone.utc
    )

    jd = _to_julian_day(
        now
    )

    positions = _calculate_positions(
        jd
    )

    transit_aspects = (
        _calculate_transit_aspects(
            positions
        )
    )

    natal_chart = (
        natal.get_natal_chart()
    )

    natal_transits = (
        _calculate_natal_transits(
            positions,
            natal_chart,
        )
    )

    return {
        "status": "ok",

        "generated_at":
            now.isoformat(),

        "current_positions":
            positions,

        "transit_aspects":
            transit_aspects,

        "natal_transits":
            natal_transits,
    }


# =========================================================
# Compatibility with advisor
# =========================================================

def detect_aspects(
    natal_chart=None,
):

    if natal_chart is None:
        natal_chart = (
            natal.get_natal_chart()
        )

    analysis = (
        get_full_transit_analysis()
    )

    return analysis[
        "natal_transits"
    ]
