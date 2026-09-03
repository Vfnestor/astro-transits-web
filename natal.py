from pathlib import Path
from datetime import datetime, timedelta, timezone
import math
import re

import swisseph as swe


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
EPHE_PATH = BASE_DIR / "ephe"

swe.set_ephe_path(str(EPHE_PATH))


# ============================================================
# SWISS EPHEMERIS
# ============================================================

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

NODES = {
    "North Node": swe.MEAN_NODE,
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
}


PLANET_SYMBOL = {
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


SIGNS = [
    ("Aries", "حمل"),
    ("Taurus", "ثور"),
    ("Gemini", "جوزا"),
    ("Cancer", "سرطان"),
    ("Leo", "اسد"),
    ("Virgo", "سنبله"),
    ("Libra", "میزان"),
    ("Scorpio", "عقرب"),
    ("Sagittarius", "قوس"),
    ("Capricorn", "جدی"),
    ("Aquarius", "دلو"),
    ("Pisces", "حوت"),
]


ASPECTS = [
    ("conjunction", "هم‌نشینی", 0, 8),
    ("opposition", "مقابله", 180, 8),
    ("trine", "تثلیث", 120, 7),
    ("square", "تربیع", 90, 7),
    ("sextile", "تسدیس", 60, 5),
    ("quincunx", "کوینکانکس", 150, 3),
]


HOUSE_SYSTEM = b"P"


# ============================================================
# ABJAD
# ============================================================

ABJAD = {
    "ا": 1,
    "أ": 1,
    "إ": 1,
    "آ": 1,
    "ب": 2,
    "ج": 3,
    "د": 4,
    "ه": 5,
    "ة": 5,
    "و": 6,
    "ز": 7,
    "ح": 8,
    "ط": 9,
    "ی": 10,
    "ي": 10,
    "ى": 10,
    "ک": 20,
    "ك": 20,
    "ل": 30,
    "م": 40,
    "ن": 50,
    "س": 60,
    "ع": 70,
    "ف": 80,
    "ص": 90,
    "ق": 100,
    "ر": 200,
    "ش": 300,
    "ت": 400,
    "ث": 500,
    "خ": 600,
    "ذ": 700,
    "ض": 800,
    "ظ": 900,
    "غ": 1000,
}


def normalize_name(text):
    if not text:
        return ""

    return (
        str(text)
        .strip()
        .replace("ي", "ی")
        .replace("ى", "ی")
        .replace("ك", "ک")
        .replace("ۀ", "ه")
        .replace("ة", "ه")
    )


def abjad_value(text):
    text = normalize_name(text)

    total = 0
    supported = 0

    for char in text:
        if char in ABJAD:
            total += ABJAD[char]
            supported += 1

    return total, supported


def reduce_number(number):
    number = abs(int(number))

    while number > 9 and number not in (11, 22, 33):
        number = sum(int(x) for x in str(number))

    return number


def life_path_number(year, month, day):
    digits = f"{year:04d}{month:02d}{day:02d}"
    total = sum(int(x) for x in digits)

    return reduce_number(total)


def calculate_numerology(
    first_name,
    family_name,
    year,
    month,
    day,
):
    first_name = normalize_name(first_name)
    family_name = normalize_name(family_name)

    full_name = f"{first_name} {family_name}".strip()

    first_value, first_supported = abjad_value(first_name)
    family_value, family_supported = abjad_value(family_name)
    full_value, full_supported = abjad_value(full_name)

    return {
        "system": "ابجد کبیر + عدد مسیر زندگی",

        "first_name": first_name,
        "family_name": family_name,
        "full_name": full_name,

        "first_name_abjad": first_value,
        "family_name_abjad": family_value,
        "full_name_abjad": full_value,

        "name_number": (
            reduce_number(full_value)
            if full_value
            else None
        ),

        "life_path_number": life_path_number(
            year,
            month,
            day,
        ),

        "abjad_supported_letters": full_supported,

        "abjad_warning": (
            None
            if full_supported > 0
            else
            "نام واردشده شامل حروف فارسی/عربی قابل محاسبه با ابجد نیست."
        ),
    }


# ============================================================
# HELPERS
# ============================================================

def _normalize_degree(degree):
    return float(degree) % 360.0


def _deg_to_sign(degree):
    degree = _normalize_degree(degree)

    index = int(degree // 30)

    if index >= 12:
        index = 11

    degree_in_sign = degree - (index * 30)

    sign_en, sign_fa = SIGNS[index]

    whole_degree = int(degree_in_sign)

    minutes_float = (
        degree_in_sign - whole_degree
    ) * 60

    minutes = int(minutes_float)

    seconds = (
        minutes_float - minutes
    ) * 60

    return {
        "sign": sign_en,
        "sign_fa": sign_fa,

        "degree_in_sign": degree_in_sign,

        "degree": whole_degree,
        "minute": minutes,
        "second": seconds,

        "formatted": (
            f"{whole_degree}° "
            f"{minutes:02d}′ "
            f"{seconds:04.1f}″ "
            f"{sign_fa}"
        ),
    }


def _angular_difference(a, b):
    diff = abs(a - b) % 360

    if diff > 180:
        diff = 360 - diff

    return diff


def _parse_birth_time(value):
    if isinstance(value, str):

        parts = value.strip().split(":")

        if len(parts) < 2:
            raise ValueError(
                "ساعت تولد باید به شکل HH:MM باشد."
            )

        hour = int(parts[0])
        minute = int(parts[1])

        if not (0 <= hour <= 23):
            raise ValueError(
                "ساعت تولد نامعتبر است."
            )

        if not (0 <= minute <= 59):
            raise ValueError(
                "دقیقه تولد نامعتبر است."
            )

        return hour, minute

    if isinstance(value, (list, tuple)) and len(value) >= 2:

        hour = int(value[0])
        minute = int(value[1])

        return hour, minute

    raise ValueError(
        "فرمت ساعت تولد نامعتبر است."
    )


def _parse_date(value):
    if isinstance(value, str):

        parts = value.strip().split("-")

        if len(parts) != 3:
            raise ValueError(
                "تاریخ تولد باید به شکل YYYY-MM-DD باشد."
            )

        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])

        return year, month, day

    if isinstance(value, dict):

        return (
            int(value["year"]),
            int(value["month"]),
            int(value["day"]),
        )

    raise ValueError(
        "فرمت تاریخ تولد نامعتبر است."
    )


def _validate_profile(profile):

    if not isinstance(profile, dict):
        raise ValueError(
            "پروفایل ارسال نشده است."
        )

    required = [
        "first_name",
        "family_name",
        "advisor_name",
        "birth_date",
        "birth_time",
        "city",
        "latitude",
        "longitude",
        "utc_offset",
    ]

    for key in required:

        if key not in profile:
            raise ValueError(
                f"فیلد {key} الزامی است."
            )

        if (
            profile[key] is None
            or str(profile[key]).strip() == ""
        ):
            raise ValueError(
                f"فیلد {key} نمی‌تواند خالی باشد."
            )

    latitude = float(profile["latitude"])
    longitude = float(profile["longitude"])
    utc_offset = float(profile["utc_offset"])

    if not -90 <= latitude <= 90:
        raise ValueError(
            "عرض جغرافیایی نامعتبر است."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "طول جغرافیایی نامعتبر است."
        )

    if not -14 <= utc_offset <= 14:
        raise ValueError(
            "UTC Offset نامعتبر است."
        )

    year, month, day = _parse_date(
        profile["birth_date"]
    )

    hour, minute = _parse_birth_time(
        profile["birth_time"]
    )

    datetime(
        year,
        month,
        day,
        hour,
        minute,
    )

    return (
        year,
        month,
        day,
        hour,
        minute,
        latitude,
        longitude,
        utc_offset,
    )


# ============================================================
# JULIAN DAY
# ============================================================

def _to_julian_day(
    year,
    month,
    day,
    hour,
    minute,
    utc_offset,
):

    local_dt = datetime(
        year,
        month,
        day,
        hour,
        minute,
    )

    utc_dt = (
        local_dt
        - timedelta(hours=float(utc_offset))
    )

    hour_decimal = (
        utc_dt.hour
        + utc_dt.minute / 60
        + utc_dt.second / 3600
    )

    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour_decimal,
    )


# ============================================================
# JALALI CONVERSION
# ============================================================

def _gregorian_to_jalali(
    gy,
    gm,
    gd,
):

    g_days_in_month = [
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31
    ]

    j_days_in_month = [
        31, 31, 31, 31, 31, 31,
        30, 30, 30, 30, 30, 29
    ]

    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = (
        365 * gy2
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
    )

    for i in range(gm2):
        g_day_no += g_days_in_month[i]

    if gm2 > 1 and (
        gy % 4 == 0
        and (
            gy % 100 != 0
            or gy % 400 == 0
        )
    ):
        g_day_no += 1

    g_day_no += gd2

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053

    j_day_no %= 12053

    jy = (
        979
        + 33 * j_np
        + 4 * (j_day_no // 1461)
    )

    j_day_no %= 1461

    if j_day_no >= 366:

        jy += (
            j_day_no - 1
        ) // 365

        j_day_no = (
            j_day_no - 1
        ) % 365

    for i in range(11):

        if j_day_no < j_days_in_month[i]:

            jm = i + 1
            jd = j_day_no + 1

            return jy, jm, jd

        j_day_no -= j_days_in_month[i]

    return (
        jy,
        12,
        j_day_no + 1,
    )


def _persian_digits(text):

    return str(text).translate(
        str.maketrans(
            "0123456789",
            "۰۱۲۳۴۵۶۷۸۹",
        )
    )


def _persian_date(
    year,
    month,
    day,
):

    jy, jm, jd = _gregorian_to_jalali(
        year,
        month,
        day,
    )

    months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]

    return (
        f"{_persian_digits(jd)} "
        f"{months[jm - 1]} "
        f"{_persian_digits(jy)}"
    )


# ============================================================
# PLANETS
# ============================================================

def _calculate_planets(jd):

    result = {}

    for name, planet_id in PLANETS.items():

        values, flags = swe.calc(
            jd,
            planet_id,
            swe.FLG_SWIEPH | swe.FLG_SPEED,
        )

        longitude = _normalize_degree(
            values[0]
        )

        latitude = values[1]

        speed = values[3]

        position = _deg_to_sign(
            longitude
        )

        result[name] = {
            "longitude": longitude,

            "sign": position["sign"],
            "sign_fa": position["sign_fa"],

            "degree_in_sign":
                position["degree_in_sign"],

            "degree":
                position["degree"],

            "minute":
                position["minute"],

            "second":
                position["second"],

            "formatted":
                position["formatted"],

            "latitude":
                latitude,

            "speed":
                speed,

            "retrograde":
                speed < 0,

            "name_fa":
                PLANET_FA[name],

            "symbol":
                PLANET_SYMBOL[name],
        }

    return result


# ============================================================
# NODES
# ============================================================

def _calculate_nodes(jd):

    result = {}

    values, flags = swe.calc(
        jd,
        swe.MEAN_NODE,
        swe.FLG_SWIEPH | swe.FLG_SPEED,
    )

    north_lon = _normalize_degree(
        values[0]
    )

    south_lon = _normalize_degree(
        north_lon + 180
    )

    for name, longitude in [
        ("North Node", north_lon),
        ("South Node", south_lon),
    ]:

        position = _deg_to_sign(
            longitude
        )

        result[name] = {
            "longitude": longitude,

            "sign": position["sign"],
            "sign_fa": position["sign_fa"],

            "degree_in_sign":
                position["degree_in_sign"],

            "degree":
                position["degree"],

            "minute":
                position["minute"],

            "second":
                position["second"],

            "formatted":
                position["formatted"],

            "latitude": 0.0,

            "speed": (
                values[3]
                if name == "North Node"
                else values[3]
            ),

            "retrograde": (
                values[3] < 0
            ),

            "name_fa":
                PLANET_FA[name],

            "symbol":
                PLANET_SYMBOL[name],
        }

    return result


# ============================================================
# HOUSES
# ============================================================

def _calculate_houses(
    jd,
    latitude,
    longitude,
):

    cusps, ascmc = swe.houses(
        jd,
        latitude,
        longitude,
        HOUSE_SYSTEM,
    )

    houses = {}

    for i in range(12):

        house_number = i + 1

        longitude_value = _normalize_degree(
            cusps[i]
        )

        position = _deg_to_sign(
            longitude_value
        )

        houses[str(house_number)] = {
            "house": house_number,

            "name_fa":
                f"خانه {house_number}",

            "longitude":
                longitude_value,

            "sign":
                position["sign"],

            "sign_fa":
                position["sign_fa"],

            "degree_in_sign":
                position["degree_in_sign"],

            "degree":
                position["degree"],

            "minute":
                position["minute"],

            "second":
                position["second"],

            "formatted":
                position["formatted"],
        }

    asc = _normalize_degree(
        ascmc[0]
    )

    mc = _normalize_degree(
        ascmc[1]
    )

    return houses, asc, mc


# ============================================================
# HOUSE ASSIGNMENT
# ============================================================

def _find_house(
    longitude,
    cusps,
):

    longitude = _normalize_degree(
        longitude
    )

    for i in range(12):

        start = _normalize_degree(
            cusps[i]
        )

        end = _normalize_degree(
            cusps[(i + 1) % 12]
        )

        if start < end:

            if start <= longitude < end:
                return i + 1

        else:

            if (
                longitude >= start
                or longitude < end
            ):
                return i + 1

    return 12


def _assign_houses(
    planets,
    nodes,
    jd,
    latitude,
    longitude,
):

    cusps, ascmc = swe.houses(
        jd,
        latitude,
        longitude,
        HOUSE_SYSTEM,
    )

    for data in planets.values():

        data["house"] = _find_house(
            data["longitude"],
            cusps,
        )

    for data in nodes.values():

        data["house"] = _find_house(
            data["longitude"],
            cusps,
        )

    return planets, nodes


# ============================================================
# ASPECTS
# ============================================================

def _find_aspect(
    longitude_a,
    longitude_b,
):

    difference = _angular_difference(
        longitude_a,
        longitude_b,
    )

    best = None

    for (
        aspect_name,
        aspect_fa,
        exact_degree,
        orb_limit,
    ) in ASPECTS:

        orb = abs(
            difference - exact_degree
        )

        if orb <= orb_limit:

            candidate = {
                "aspect": aspect_name,
                "aspect_fa": aspect_fa,
                "degree": exact_degree,
                "orb": orb,
            }

            if (
                best is None
                or candidate["orb"]
                < best["orb"]
            ):
                best = candidate

    return best


def _calculate_aspects(
    planets,
    nodes,
):

    targets = {}

    for name, data in planets.items():

        targets[name] = {
            **data,
            "target_type": "planet",
        }

    for name, data in nodes.items():

        targets[name] = {
            **data,
            "target_type": "node",
        }

    names = list(targets.keys())

    aspects = []

    for i in range(len(names)):

        name_a = names[i]

        for j in range(
            i + 1,
            len(names),
        ):

            name_b = names[j]

            data_a = targets[name_a]
            data_b = targets[name_b]

            aspect = _find_aspect(
                data_a["longitude"],
                data_b["longitude"],
            )

            if aspect is None:
                continue

            aspects.append({
                "planet_a": name_a,
                "planet_a_fa":
                    data_a.get(
                        "name_fa",
                        PLANET_FA.get(
                            name_a,
                            name_a,
                        ),
                    ),

                "planet_b": name_b,
                "planet_b_fa":
                    data_b.get(
                        "name_fa",
                        PLANET_FA.get(
                            name_b,
                            name_b,
                        ),
                    ),

                "aspect":
                    aspect["aspect"],

                "aspect_fa":
                    aspect["aspect_fa"],

                "degree":
                    aspect["degree"],

                "orb":
                    aspect["orb"],
            })

    aspects.sort(
        key=lambda item: item["orb"]
    )

    return aspects


# ============================================================
# ANGLE ASPECTS
# ============================================================

def _calculate_angle_aspects(
    planets,
    nodes,
    asc,
    mc,
):

    angles = {
        "Ascendant": {
            "longitude": asc,
            "name_fa": "طالع",
        },
        "MC": {
            "longitude": mc,
            "name_fa": "وسط آسمان",
        },
    }

    result = []

    targets = {}

    targets.update(planets)
    targets.update(nodes)

    for planet_name, planet_data in targets.items():

        for angle_name, angle_data in angles.items():

            aspect = _find_aspect(
                planet_data["longitude"],
                angle_data["longitude"],
            )

            if aspect is None:
                continue

            result.append({
                "planet": planet_name,

                "planet_fa":
                    planet_data.get(
                        "name_fa",
                        PLANET_FA.get(
                            planet_name,
                            planet_name,
                        ),
                    ),

                "angle":
                    angle_name,

                "angle_fa":
                    angle_data["name_fa"],

                "aspect":
                    aspect["aspect"],

                "aspect_fa":
                    aspect["aspect_fa"],

                "degree":
                    aspect["degree"],

                "orb":
                    aspect["orb"],
            })

    result.sort(
        key=lambda item: item["orb"]
    )

    return result


# ============================================================
# PLANET + HOUSE DATA
# ============================================================

def _build_house_summary(
    houses,
    planets,
    nodes,
):

    summary = {}

    for house_number in range(1, 13):

        house_key = str(house_number)

        house = houses[house_key]

        occupants = []

        for name, data in planets.items():

            if data.get("house") == house_number:

                occupants.append({
                    "name": name,
                    "name_fa":
                        data.get(
                            "name_fa",
                            PLANET_FA.get(
                                name,
                                name,
                            ),
                        ),
                    "symbol":
                        data.get(
                            "symbol",
                            "",
                        ),
                })

        for name, data in nodes.items():

            if data.get("house") == house_number:

                occupants.append({
                    "name": name,
                    "name_fa":
                        data.get(
                            "name_fa",
                            PLANET_FA.get(
                                name,
                                name,
                            ),
                        ),
                    "symbol":
                        data.get(
                            "symbol",
                            "",
                        ),
                })

        summary[house_key] = {
            **house,
            "occupants": occupants,
        }

    return summary


# ============================================================
# NATAL CHART
# ============================================================

def get_natal_chart(profile):

    (
        year,
        month,
        day,
        hour,
        minute,
        latitude,
        longitude,
        utc_offset,
    ) = _validate_profile(profile)

    # --------------------------------------------------------
    # Julian Day
    # --------------------------------------------------------

    jd = _to_julian_day(
        year,
        month,
        day,
        hour,
        minute,
        utc_offset,
    )

    # --------------------------------------------------------
    # Planets
    # --------------------------------------------------------

    planets = _calculate_planets(
        jd
    )

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    nodes = _calculate_nodes(
        jd
    )

    # --------------------------------------------------------
    # Houses
    # --------------------------------------------------------

    houses, asc, mc = _calculate_houses(
        jd,
        latitude,
        longitude,
    )

    # --------------------------------------------------------
    # Assign houses
    # --------------------------------------------------------

    planets, nodes = _assign_houses(
        planets,
        nodes,
        jd,
        latitude,
        longitude,
    )

    # --------------------------------------------------------
    # Aspects
    # --------------------------------------------------------

    aspects = _calculate_aspects(
        planets,
        nodes,
    )

    # --------------------------------------------------------
    # Angle aspects
    # --------------------------------------------------------

    angle_aspects = _calculate_angle_aspects(
        planets,
        nodes,
        asc,
        mc,
    )

    # --------------------------------------------------------
    # ASC / MC positions
    # --------------------------------------------------------

    asc_position = _deg_to_sign(
        asc
    )

    mc_position = _deg_to_sign(
        mc
    )

    # --------------------------------------------------------
    # House summary
    # --------------------------------------------------------

    house_summary = _build_house_summary(
        houses,
        planets,
        nodes,
    )

    # --------------------------------------------------------
    # Numerology
    # --------------------------------------------------------

    numerology = calculate_numerology(
        profile["first_name"],
        profile["family_name"],
        year,
        month,
        day,
    )

    # --------------------------------------------------------
    # Birth date
    # --------------------------------------------------------

    gregorian_date = (
        f"{year:04d}-"
        f"{month:02d}-"
        f"{day:02d}"
    )

    persian_date = _persian_date(
        year,
        month,
        day,
    )

    birth_time = (
        f"{hour:02d}:{minute:02d}"
    )

    # --------------------------------------------------------
    # Angles
    #
    # Multiple aliases are intentionally provided so that
    # frontend and transit modules can use different naming
    # conventions safely.
    # --------------------------------------------------------

    asc_data = {
        "longitude": asc,
        **asc_position,
        "name": "Ascendant",
        "name_fa": "طالع",
        "symbol": "ASC",
    }

    mc_data = {
        "longitude": mc,
        **mc_position,
        "name": "MC",
        "name_fa": "وسط آسمان",
        "symbol": "MC",
    }

    # --------------------------------------------------------
    # Final chart
    # --------------------------------------------------------

    return {

        "status": "ok",

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        # ----------------------------------------------------
        # Person
        # ----------------------------------------------------

        "person": {

            "first_name":
                profile["first_name"],

            "family_name":
                profile["family_name"],

            "full_name":
                (
                    f'{profile["first_name"]} '
                    f'{profile["family_name"]}'
                ).strip(),

            "advisor_name":
                profile.get(
                    "advisor_name",
                    "",
                ),
        },

        # ----------------------------------------------------
        # Birth data
        # ----------------------------------------------------

        "birth_data": {

            "date":
                gregorian_date,

            "date_gregorian":
                gregorian_date,

            "date_persian":
                persian_date,

            "time":
                birth_time,

            "city":
                profile["city"],

            "latitude":
                latitude,

            "longitude":
                longitude,

            "utc_offset":
                utc_offset,

            "timezone":
                f"UTC{utc_offset:+g}",
        },

        # ----------------------------------------------------
        # Zodiac
        # ----------------------------------------------------

        "zodiac": {

            "type":
                "tropical",

            "name_fa":
                "تروپیکال",
        },

        # ----------------------------------------------------
        # House system
        # ----------------------------------------------------

        "house_system": {

            "type":
                "Placidus",

            "name_fa":
                "پلاسیدوس",
        },

        # ----------------------------------------------------
        # Julian Day
        # ----------------------------------------------------

        "julian_day":
            jd,

        # ----------------------------------------------------
        # Angles
        # ----------------------------------------------------

        "angles": {

            # Canonical
            "ascendant":
                asc_data,

            "mc":
                mc_data,

            # Compatibility aliases
            "ASC":
                asc_data,

            "asc":
                asc_data,

            "MC":
                mc_data,

            "midheaven":
                mc_data,
        },

        # ----------------------------------------------------
        # Houses
        # ----------------------------------------------------

        "houses":
            houses,

        "house_summary":
            house_summary,

        # ----------------------------------------------------
        # Planets
        # ----------------------------------------------------

        "planets":
            planets,

        # ----------------------------------------------------
        # Nodes
        # ----------------------------------------------------

        "nodes":
            nodes,

        # ----------------------------------------------------
        # Natal aspects
        # ----------------------------------------------------

        "aspects":
            aspects,

        "angle_aspects":
            angle_aspects,

        # ----------------------------------------------------
        # Numerology
        # ----------------------------------------------------

        "numerology":
            numerology,
    }


# ============================================================
# OPTIONAL ALIASES
# ============================================================

def calculate_natal_chart(profile):
    """
    Compatibility alias.

    Allows callers using calculate_natal_chart()
    to use the same natal engine.
    """

    return get_natal_chart(profile)


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    # Minimal internal test profile.
    # This block runs only when executing:
    #
    # python natal.py
    #
    # It does not affect FastAPI.

    test_profile = {
        "first_name": "وحید",
        "family_name": "فدایی طیولا",
        "advisor_name": "مشاور نجومی",
        "birth_date": "1993-03-11",
        "birth_time": "20:35",
        "city": "اندیشه",
        "latitude": 35.68,
        "longitude": 51.02,
        "utc_offset": 3.5,
    }

    try:

        chart = get_natal_chart(
            test_profile
        )

        print(
            "Natal chart calculated successfully."
        )

        print(
            "ASC:",
            chart["angles"]["ascendant"][
                "formatted"
            ],
        )

        print(
            "MC:",
            chart["angles"]["mc"][
                "formatted"
            ],
        )

        print(
            "Planets:",
            len(chart["planets"]),
        )

        print(
            "Houses:",
            len(chart["houses"]),
        )

        print(
            "Aspects:",
            len(chart["aspects"]),
        )

    except Exception as exc:

        print(
            "Natal chart calculation failed:"
        )

        print(
            repr(exc)
        )
