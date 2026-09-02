import swisseph as swe

from datetime import datetime, timedelta, timezone


# =========================================================
# Swiss Ephemeris
# =========================================================

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent

swe.set_ephe_path(
    str(BASE_DIR / "ephe")
)


# =========================================================
# اطلاعات تولد
# =========================================================

BIRTH_DATE = (1995, 3, 11)
BIRTH_TIME = (20, 35)

BIRTH_LAT = 35.7063066
BIRTH_LON = 51.4509970

# تهران در 11 مارس 1995
# UTC+3:30
BIRTH_UTC_OFFSET = 3.5


# =========================================================
# سیارات
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


# =========================================================
# گره‌ها
# =========================================================

NODES = {
    "North Node": swe.MEAN_NODE,
}


# =========================================================
# برج‌ها
# =========================================================

SIGNS = [
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


SIGN_NAMES_FA = {
    "Aries": "حمل",
    "Taurus": "ثور",
    "Gemini": "جوزا",
    "Cancer": "سرطان",
    "Leo": "اسد",
    "Virgo": "سنبله",
    "Libra": "میزان",
    "Scorpio": "عقرب",
    "Sagittarius": "قوس",
    "Capricorn": "جدی",
    "Aquarius": "دلو",
    "Pisces": "حوت",
}


PLANET_NAMES_FA = {
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
}


PLANET_SYMBOLS = {
    "Sun": "☀",
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
}


# =========================================================
# خانه‌ها
# =========================================================

HOUSE_SYSTEM = b"P"


HOUSE_NAMES_FA = {
    1: "خانه اول",
    2: "خانه دوم",
    3: "خانه سوم",
    4: "خانه چهارم",
    5: "خانه پنجم",
    6: "خانه ششم",
    7: "خانه هفتم",
    8: "خانه هشتم",
    9: "خانه نهم",
    10: "خانه دهم",
    11: "خانه یازدهم",
    12: "خانه دوازدهم",
}


# =========================================================
# جنبه‌ها
# =========================================================

ASPECTS = {
    "conjunction": {
        "angle": 0,
        "orb": 8.0,
        "name_fa": "هم‌نشینی",
    },

    "opposition": {
        "angle": 180,
        "orb": 8.0,
        "name_fa": "مقابله",
    },

    "trine": {
        "angle": 120,
        "orb": 7.0,
        "name_fa": "تثلیث",
    },

    "square": {
        "angle": 90,
        "orb": 7.0,
        "name_fa": "تربیع",
    },

    "sextile": {
        "angle": 60,
        "orb": 5.0,
        "name_fa": "تسدیس",
    },

    "quincunx": {
        "angle": 150,
        "orb": 3.0,
        "name_fa": "کوینکانکس",
    },
}


# =========================================================
# ابزارها
# =========================================================

def _normalize_degree(deg):
    return float(deg) % 360.0


def _deg_to_sign(deg):

    deg = _normalize_degree(deg)

    sign_index = int(deg // 30)

    degree_in_sign = deg % 30

    sign = SIGNS[sign_index]

    return sign, degree_in_sign


def _format_position(deg):

    deg = _normalize_degree(deg)

    sign, degree_in_sign = _deg_to_sign(deg)

    degree = int(degree_in_sign)

    minute_float = (
        degree_in_sign - degree
    ) * 60

    minute = int(minute_float)

    second = round(
        (minute_float - minute) * 60,
        2,
    )

    return {
        "longitude": round(deg, 6),
        "sign": sign,
        "sign_fa": SIGN_NAMES_FA[sign],
        "degree_in_sign": round(
            degree_in_sign,
            6,
        ),
        "degree": degree,
        "minute": minute,
        "second": second,
        "formatted": (
            f"{degree}° "
            f"{minute:02d}′ "
            f"{second:04.1f}″ "
            f"{SIGN_NAMES_FA[sign]}"
        ),
    }


def _angular_difference(a, b):

    diff = abs(
        _normalize_degree(a)
        - _normalize_degree(b)
    )

    if diff > 180:
        diff = 360 - diff

    return diff


# =========================================================
# Local → UTC
# =========================================================

def _to_julian_day(
    year,
    month,
    day,
    hour,
    minute,
):

    local_datetime = datetime(
        year,
        month,
        day,
        hour,
        minute,
    )

    utc_datetime = (
        local_datetime
        - timedelta(
            hours=BIRTH_UTC_OFFSET
        )
    )

    utc_hour = (
        utc_datetime.hour
        + utc_datetime.minute / 60
        + utc_datetime.second / 3600
    )

    return swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_hour,
        swe.GREG_CAL,
    )


# =========================================================
# سیارات
# =========================================================

def _calculate_planets(jd):

    positions = {}

    for name, code in PLANETS.items():

        result = swe.calc(
            jd,
            code,
        )

        values = result[0]

        lon = float(values[0])
        lat = float(values[1])
        speed = float(values[3])

        position = _format_position(
            lon
        )

        position["latitude"] = lat
        position["speed"] = speed
        position["retrograde"] = speed < 0
        position["name_fa"] = PLANET_NAMES_FA[name]
        position["symbol"] = PLANET_SYMBOLS[name]

        positions[name] = position

    return positions


# =========================================================
# Nodes
# =========================================================

def _calculate_nodes(jd):

    result = swe.calc(
        jd,
        swe.MEAN_NODE,
    )

    north_lon = float(
        result[0][0]
    )

    south_lon = _normalize_degree(
        north_lon + 180
    )

    north = _format_position(
        north_lon
    )

    south = _format_position(
        south_lon
    )

    north["name_fa"] = "گره شمالی"
    north["symbol"] = "☊"

    south["name_fa"] = "گره جنوبی"
    south["symbol"] = "☋"

    return {
        "North Node": north,
        "South Node": south,
    }


# =========================================================
# Houses
# =========================================================

def _calculate_houses(jd):

    houses, ascmc = swe.houses(
        jd,
        BIRTH_LAT,
        BIRTH_LON,
        HOUSE_SYSTEM,
    )

    house_data = {}

    for index in range(12):

        number = index + 1

        cusp = float(
            houses[index]
        )

        house_data[str(number)] = {
            "house": number,
            "name_fa": HOUSE_NAMES_FA[number],
            **_format_position(cusp),
        }

    ascendant = _format_position(
        float(ascmc[0])
    )

    mc = _format_position(
        float(ascmc[1])
    )

    return {
        "houses": house_data,
        "ascendant": ascendant,
        "mc": mc,
    }


# =========================================================
# Find house
# =========================================================

def _find_house(
    longitude,
    houses,
):

    longitude = _normalize_degree(
        longitude
    )

    cusps = [
        float(
            houses[str(i)]["longitude"]
        )
        for i in range(1, 13)
    ]

    for i in range(12):

        start = cusps[i]
        end = cusps[(i + 1) % 12]

        if i == 11:

            if (
                longitude >= start
                or longitude < end
            ):
                return 12

        else:

            if (
                start <= longitude < end
            ):
                return i + 1

    return 12


# =========================================================
# Assign houses
# =========================================================

def _assign_houses(
    bodies,
    houses,
):

    for name, data in bodies.items():

        house = _find_house(
            data["longitude"],
            houses,
        )

        data["house"] = house
        data["house_name_fa"] = (
            HOUSE_NAMES_FA[house]
        )

    return bodies


# =========================================================
# Natal aspects
# =========================================================

def _calculate_aspects(
    bodies,
):

    aspects = []

    names = list(
        bodies.keys()
    )

    for i in range(len(names)):

        for j in range(
            i + 1,
            len(names),
        ):

            p1 = names[i]
            p2 = names[j]

            lon1 = bodies[p1][
                "longitude"
            ]

            lon2 = bodies[p2][
                "longitude"
            ]

            diff = _angular_difference(
                lon1,
                lon2,
            )

            for aspect_name, info in ASPECTS.items():

                target = info["angle"]

                orb = abs(
                    diff - target
                )

                if orb <= info["orb"]:

                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "planet1_fa": PLANET_NAMES_FA[p1],
                        "planet2_fa": PLANET_NAMES_FA[p2],
                        "aspect": aspect_name,
                        "aspect_fa": info["name_fa"],
                        "angle": target,
                        "exact_difference": round(
                            diff,
                            4,
                        ),
                        "orb": round(
                            orb,
                            4,
                        ),
                    })

                    break

    aspects.sort(
        key=lambda x: x["orb"]
    )

    return aspects


# =========================================================
# Full natal chart
# =========================================================

def get_natal_chart():

    jd = _to_julian_day(
        BIRTH_DATE[0],
        BIRTH_DATE[1],
        BIRTH_DATE[2],
        BIRTH_TIME[0],
        BIRTH_TIME[1],
    )

    planets = _calculate_planets(
        jd
    )

    nodes = _calculate_nodes(
        jd
    )

    house_data = _calculate_houses(
        jd
    )

    houses = house_data["houses"]

    planets = _assign_houses(
        planets,
        houses,
    )

    nodes = _assign_houses(
        nodes,
        houses,
    )

    all_bodies = {}

    all_bodies.update(planets)
    all_bodies.update(nodes)

    aspects = _calculate_aspects(
        all_bodies
    )

    generated_at = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    return {
        "status": "ok",

        "generated_at": generated_at,

        "birth_data": {
            "date": {
                "year": BIRTH_DATE[0],
                "month": BIRTH_DATE[1],
                "day": BIRTH_DATE[2],
            },

            "date_fa": "۲۰ اسفند ۱۳۷۳",

            "time": {
                "hour": BIRTH_TIME[0],
                "minute": BIRTH_TIME[1],
            },

            "time_fa": "۲۰:۳۵",

            "utc_offset": BIRTH_UTC_OFFSET,

            "location": {
                "city": "تهران",
                "latitude": BIRTH_LAT,
                "longitude": BIRTH_LON,
            },
        },

        "zodiac": {
            "type": "tropical",
            "name_fa": "تروپیکال",
        },

        "house_system": {
            "type": "Placidus",
            "name_fa": "پلاسیدوس",
        },

        "julian_day": jd,

        "angles": {
            "ascendant": house_data["ascendant"],
            "mc": house_data["mc"],
        },

        "houses": houses,

        "planets": planets,

        "nodes": nodes,

        "aspects": aspects,
    }
