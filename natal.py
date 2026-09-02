import swisseph as swe
from datetime import datetime, timedelta

# =========================================================
# Swiss Ephemeris
# =========================================================

swe.set_ephe_path("ephe")


# =========================================================
# اطلاعات تولد نمونه
# 21 March 1990 - 12:00 - Tehran
# =========================================================

BIRTH_DATE = (1990, 3, 21)
BIRTH_TIME = (12, 0)

BIRTH_LAT = 35.6892
BIRTH_LON = 51.3890

# ساعت رسمی تهران در تاریخ نمونه
# برای تبدیل ساعت محلی به UTC
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
# گره‌های ماه
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


# =========================================================
# خانه‌ها
# =========================================================

HOUSE_SYSTEM = b"P"

HOUSE_NAMES = {
    1: "First House",
    2: "Second House",
    3: "Third House",
    4: "Fourth House",
    5: "Fifth House",
    6: "Sixth House",
    7: "Seventh House",
    8: "Eighth House",
    9: "Ninth House",
    10: "Tenth House",
    11: "Eleventh House",
    12: "Twelfth House",
}


# =========================================================
# جنبه‌ها
# =========================================================

ASPECTS = {
    "conjunction": {
        "angle": 0,
        "orb": 8.0,
    },
    "opposition": {
        "angle": 180,
        "orb": 8.0,
    },
    "trine": {
        "angle": 120,
        "orb": 7.0,
    },
    "square": {
        "angle": 90,
        "orb": 7.0,
    },
    "sextile": {
        "angle": 60,
        "orb": 5.0,
    },
    "quincunx": {
        "angle": 150,
        "orb": 3.0,
    },
}


# =========================================================
# ابزارهای ریاضی
# =========================================================

def _normalize_degree(deg: float) -> float:
    """
    تبدیل درجه به بازه 0 تا 360
    """
    return float(deg) % 360.0


def _deg_to_sign(deg: float):
    """
    تبدیل طول دایره البروج به برج و درجه داخل برج.
    """

    deg = _normalize_degree(deg)

    sign_index = int(deg // 30)
    degree_in_sign = deg % 30

    sign = SIGNS[sign_index]

    return sign, degree_in_sign


def _format_position(deg: float):
    """
    ساخت اطلاعات کامل یک موقعیت نجومی.
    """

    deg = _normalize_degree(deg)

    sign, degree_in_sign = _deg_to_sign(deg)

    degree = int(degree_in_sign)
    minute_float = (degree_in_sign - degree) * 60
    minute = int(minute_float)

    second = round((minute_float - minute) * 60, 2)

    return {
        "longitude": deg,
        "sign": sign,
        "sign_fa": SIGN_NAMES_FA.get(sign, sign),
        "degree_in_sign": degree_in_sign,
        "degree": degree,
        "minute": minute,
        "second": second,
    }


def _angular_difference(a: float, b: float) -> float:
    """
    کوتاه‌ترین فاصله بین دو درجه.
    """

    a = _normalize_degree(a)
    b = _normalize_degree(b)

    diff = abs(a - b)

    if diff > 180:
        diff = 360 - diff

    return diff


# =========================================================
# تبدیل ساعت محلی به Julian Day
# =========================================================

def _to_julian_day(year, month, day, hour, minute):
    """
    تبدیل تاریخ و ساعت محلی تولد به Julian Day.
    """

    local_datetime = datetime(
        year,
        month,
        day,
        hour,
        minute,
    )

    utc_datetime = local_datetime - timedelta(
        hours=BIRTH_UTC_OFFSET
    )

    utc_hour = (
        utc_datetime.hour
        + utc_datetime.minute / 60.0
        + utc_datetime.second / 3600.0
    )

    return swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_hour,
        swe.GREG_CAL,
    )


# =========================================================
# محاسبه موقعیت سیارات
# =========================================================

def _calculate_planets(jd):
    """
    محاسبه موقعیت سیارات.
    """

    positions = {}

    for name, code in PLANETS.items():

        result = swe.calc(jd, code)

        # ساختار pyswisseph:
        # result[0] = tuple موقعیت‌ها
        # result[0][0] = longitude
        # result[0][1] = latitude

        lon = float(result[0][0])
        lat = float(result[0][1])

        position = _format_position(lon)

        position["latitude"] = lat

        positions[name] = position

    return positions


# =========================================================
# محاسبه گره‌های ماه
# =========================================================

def _calculate_nodes(jd):
    """
    محاسبه گره شمالی و جنوبی.
    """

    result = swe.calc(jd, swe.MEAN_NODE)

    north_lon = float(result[0][0])

    south_lon = _normalize_degree(
        north_lon + 180
    )

    north_position = _format_position(north_lon)
    south_position = _format_position(south_lon)

    return {
        "North Node": north_position,
        "South Node": south_position,
    }


# =========================================================
# محاسبه خانه‌ها و زوایا
# =========================================================

def _calculate_houses(jd):
    """
    محاسبه 12 خانه، Ascendant و MC.
    سیستم خانه‌ها: Placidus
    """

    houses, ascmc = swe.houses(
        jd,
        BIRTH_LAT,
        BIRTH_LON,
        HOUSE_SYSTEM,
    )

    house_data = {}

    for index in range(12):

        cusp_degree = float(houses[index])

        house_number = index + 1

        position = _format_position(cusp_degree)

        house_data[str(house_number)] = {
            "house": house_number,
            "name": HOUSE_NAMES[house_number],
            **position,
        }

    ascendant = float(ascmc[0])
    mc = float(ascmc[1])

    return {
        "houses": house_data,
        "ascendant": _format_position(ascendant),
        "mc": _format_position(mc),
    }


# =========================================================
# تعیین خانه یک سیاره
# =========================================================

def _find_house(longitude: float, houses: dict) -> int:
    """
    پیدا کردن خانه‌ای که سیاره داخل آن قرار دارد.
    """

    longitude = _normalize_degree(longitude)

    cusps = [
        float(houses[str(i)]["longitude"])
        for i in range(1, 13)
    ]

    for i in range(12):

        start = cusps[i]
        end = cusps[(i + 1) % 12]

        if i == 11:

            if longitude >= start or longitude < end:
                return 12

        else:

            if start <= longitude < end:
                return i + 1

    return 12


# =========================================================
# اضافه کردن خانه به سیارات
# =========================================================

def _assign_houses(planet_positions, houses):
    """
    مشخص کردن خانه هر سیاره.
    """

    for name, data in planet_positions.items():

        house_number = _find_house(
            data["longitude"],
            houses,
        )

        data["house"] = house_number
        data["house_name"] = HOUSE_NAMES[house_number]

    return planet_positions


# =========================================================
# محاسبه جنبه‌های چارت تولد
# =========================================================

def _calculate_aspects(planet_positions):
    """
    پیدا کردن جنبه‌های اصلی بین سیارات.
    """

    aspects = []

    names = list(planet_positions.keys())

    for i in range(len(names)):

        for j in range(i + 1, len(names)):

            planet1 = names[i]
            planet2 = names[j]

            lon1 = planet_positions[planet1]["longitude"]
            lon2 = planet_positions[planet2]["longitude"]

            diff = _angular_difference(
                lon1,
                lon2,
            )

            for aspect_name, aspect_info in ASPECTS.items():

                angle = aspect_info["angle"]
                orb_limit = aspect_info["orb"]

                orb = abs(diff - angle)

                if orb <= orb_limit:

                    aspects.append({
                        "planet1": planet1,
                        "planet2": planet2,
                        "aspect": aspect_name,
                        "angle": angle,
                        "exact_difference": diff,
                        "orb": orb,
                    })

                    break

    return aspects


# =========================================================
# ساخت چارت کامل
# =========================================================

def get_natal_chart():

    jd = _to_julian_day(
        BIRTH_DATE[0],
        BIRTH_DATE[1],
        BIRTH_DATE[2],
        BIRTH_TIME[0],
        BIRTH_TIME[1],
    )

    # سیارات
    planets = _calculate_planets(jd)

    # گره‌ها
    nodes = _calculate_nodes(jd)

    # خانه‌ها
    house_data = _calculate_houses(jd)

    houses = house_data["houses"]

    ascendant = house_data["ascendant"]
    mc = house_data["mc"]

    # اضافه کردن خانه به سیارات
    planets = _assign_houses(
        planets,
        houses,
    )

    # اضافه کردن خانه به گره‌ها
    nodes = _assign_houses(
        nodes,
        houses,
    )

    # همه اجرام برای محاسبه جنبه‌ها
    all_bodies = {}

    all_bodies.update(planets)
    all_bodies.update(nodes)

    aspects = _calculate_aspects(
        all_bodies
    )

    return {
        "status": "ok",

        "generated_at": datetime.utcnow().isoformat(),

        "birth_data": {
            "date": {
                "year": BIRTH_DATE[0],
                "month": BIRTH_DATE[1],
                "day": BIRTH_DATE[2],
            },

            "time": {
                "hour": BIRTH_TIME[0],
                "minute": BIRTH_TIME[1],
            },

            "utc_offset": BIRTH_UTC_OFFSET,

            "location": {
                "latitude": BIRTH_LAT,
                "longitude": BIRTH_LON,
            },
        },

        "ayanamsa": {
            "type": "tropical",
        },

        "angles": {
            "ascendant": ascendant,
            "mc": mc,
        },

        "houses": houses,

        "planets": planets,

        "nodes": nodes,

        "aspects": aspects,
    }
