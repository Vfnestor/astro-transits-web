from datetime import datetime, timezone
from pathlib import Path

import swisseph as swe


# =========================================================
# ASTRO VAHID — EPHEMERIS ENGINE
# Version 3.3
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

def _normalize_degree(value: float) -> float:
    return float(value) % 360.0


def _degree_difference(a: float, b: float) -> float:

    diff = abs(a - b) % 360.0

    if diff > 180.0:
        diff = 360.0 - diff

    return diff


def _to_julian_day(dt: datetime) -> float:

    if dt.tzinfo is not None:
        dt = dt.astimezone(
            timezone.utc
        ).replace(
            tzinfo=None
        )

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


def _find_aspect(diff: float):

    candidates = []

    for name, data in ASPECTS.items():

        orb = abs(
            diff - data["degree"]
        )

        if orb <= data["orb"]:

            candidates.append(
                (
                    orb,
                    name,
                    data,
                )
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0]
    )

    orb, name, data = candidates[0]

    return {
        "aspect": name,
        "aspect_fa": data["fa"],
        "aspect_symbol": data["symbol"],
        "aspect_degree": data["degree"],
        "orb": round(
            orb,
            4
        ),
        "weight": data["weight"],
    }


def _format_position(
    longitude: float
) -> dict:

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

    longitude = _normalize_degree(
        longitude
    )

    sign_index = int(
        longitude // 30
    )

    degree_float = (
        longitude % 30
    )

    degree = int(
        degree_float
    )

    minutes_float = (
        degree_float - degree
    ) * 60

    minute = int(
        minutes_float
    )

    second = round(
        (
            minutes_float - minute
        ) * 60,
        1,
    )

    return {
        "longitude": round(
            longitude,
            6,
        ),
        "sign": signs[
            sign_index
        ],
        "sign_fa": signs_fa[
            sign_index
        ],
        "degree": degree,
        "minute": minute,
        "second": second,
        "formatted": (
            f"{degree}° "
            f"{minute:02d}′ "
            f"{second:04.1f}″ "
            f"{signs_fa[sign_index]}"
        ),
    }


# =========================================================
# PLANET POSITIONS
# =========================================================

def _calculate_positions(
    jd: float
):

    positions = {}

    for name, code in PLANETS.items():

        result = swe.calc(
            jd,
            code,
        )

        longitude = result[0][0]
        speed = result[0][3]

        position = _format_position(
            longitude
        )

        positions[name] = {
            "longitude":
                position["longitude"],

            "sign":
                position["sign"],

            "sign_fa":
                position["sign_fa"],

            "degree":
                position["degree"],

            "minute":
                position["minute"],

            "second":
                position["second"],

            "formatted":
                position["formatted"],

            "retrograde":
                speed < 0,

            "speed":
                round(
                    speed,
                    6,
                ),

            "planet_fa":
                PLANET_FA[name],

            "name_fa":
                PLANET_FA[name],

            "symbol":
                PLANET_SYMBOL[name],
        }

    return positions


# =========================================================
# TRANSIT → TRANSIT
# =========================================================

def _calculate_transit_aspects(
    positions: dict
):

    results = []

    names = list(
        positions.keys()
    )

    for i in range(
        len(names)
    ):

        for j in range(
            i + 1,
            len(names)
        ):

            p1 = names[i]
            p2 = names[j]

            lon1 = positions[p1].get(
                "longitude"
            )

            lon2 = positions[p2].get(
                "longitude"
            )

            if lon1 is None or lon2 is None:
                continue

            diff = _degree_difference(
                lon1,
                lon2,
            )

            aspect = _find_aspect(
                diff
            )

            if not aspect:
                continue

            results.append(
                {
                    "planet1":
                        p1,

                    "planet1_fa":
                        PLANET_FA.get(
                            p1,
                            p1
                        ),

                    "planet1_symbol":
                        PLANET_SYMBOL.get(
                            p1,
                            ""
                        ),

                    "planet2":
                        p2,

                    "planet2_fa":
                        PLANET_FA.get(
                            p2,
                            p2
                        ),

                    "planet2_symbol":
                        PLANET_SYMBOL.get(
                            p2,
                            ""
                        ),

                    "aspect":
                        aspect["aspect"],

                    "aspect_fa":
                        aspect["aspect_fa"],

                    "aspect_symbol":
                        aspect["aspect_symbol"],

                    "aspect_degree":
                        aspect["aspect_degree"],

                    "exact_diff":
                        round(
                            diff,
                            4,
                        ),

                    "orb":
                        aspect["orb"],

                    "weight":
                        aspect["weight"],
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
# NATAL TARGETS
# =========================================================

def _extract_longitude(data):

    """
    استخراج longitude از ساختارهای مختلف.

    پشتیبانی از:
        {"longitude": 123.4}
        {"position": {"longitude": 123.4}}
        {"lon": 123.4}
        {"position": {"lon": 123.4}}
    """

    if not isinstance(data, dict):
        return None

    longitude = data.get(
        "longitude"
    )

    if longitude is None:
        longitude = data.get(
            "lon"
        )

    if longitude is None:

        position = data.get(
            "position"
        )

        if isinstance(position, dict):

            longitude = position.get(
                "longitude"
            )

            if longitude is None:
                longitude = position.get(
                    "lon"
                )

    if longitude is None:
        return None

    try:
        return float(
            longitude
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _extract_natal_targets(
    natal_chart: dict
):

    targets = {}

    if not isinstance(
        natal_chart,
        dict
    ):
        return targets

    # =====================================================
    # PLANETS
    # =====================================================

    planets = natal_chart.get(
        "planets",
        {}
    )

    if isinstance(
        planets,
        dict
    ):

        planet_items = list(
            planets.items()
        )

    elif isinstance(
        planets,
        list
    ):

        planet_items = []

        for item in planets:

            if not isinstance(
                item,
                dict
            ):
                continue

            name = (
                item.get("name")
                or item.get("planet")
                or item.get("key")
            )

            if name:
                planet_items.append(
                    (
                        name,
                        item
                    )
                )

    else:

        planet_items = []


    for name, data in planet_items:

        if not isinstance(
            data,
            dict
        ):
            continue

        longitude = _extract_longitude(
            data
        )

        if longitude is None:
            continue

        targets[name] = {
            "longitude":
                longitude,

            "target_type":
                "planet",

            "house":
                data.get("house"),

            "house_name_fa":
                data.get(
                    "house_name_fa"
                ),

            "sign":
                data.get("sign"),

            "sign_fa":
                data.get(
                    "sign_fa"
                ),
        }


    # =====================================================
    # NODES
    # =====================================================

    nodes = natal_chart.get(
        "nodes",
        {}
    )

    if isinstance(
        nodes,
        dict
    ):

        node_items = list(
            nodes.items()
        )

    elif isinstance(
        nodes,
        list
    ):

        node_items = []

        for item in nodes:

            if not isinstance(
                item,
                dict
            ):
                continue

            name = (
                item.get("name")
                or item.get("node")
                or item.get("key")
            )

            if name:
                node_items.append(
                    (
                        name,
                        item
                    )
                )

    else:

        node_items = []


    for name, data in node_items:

        if not isinstance(
            data,
            dict
        ):
            continue

        longitude = _extract_longitude(
            data
        )

        if longitude is None:
            continue

        targets[name] = {
            "longitude":
                longitude,

            "target_type":
                "node",

            "house":
                data.get("house"),

            "house_name_fa":
                data.get(
                    "house_name_fa"
                ),

            "sign":
                data.get("sign"),

            "sign_fa":
                data.get(
                    "sign_fa"
                ),
        }


    # =====================================================
    # ANGLES
    # =====================================================

    angles = natal_chart.get(
        "angles",
        {}
    )

    if not isinstance(
        angles,
        dict
    ):
        angles = {}


    # =====================================================
    # ASC
    # =====================================================

    asc = (
        angles.get("ascendant")
        or angles.get("ASC")
        or angles.get("asc")
    )

    asc_lon = None

    if isinstance(
        asc,
        dict
    ):
        asc_lon = _extract_longitude(
            asc
        )

    elif asc is not None:

        try:
            asc_lon = float(
                asc
            )

        except (
            TypeError,
            ValueError,
        ):
            asc_lon = None


    if asc_lon is not None:

        asc_position = _format_position(
            asc_lon
        )

        targets["ASC"] = {
            "longitude":
                asc_position["longitude"],

            "target_type":
                "angle",

            "house":
                1,

            "house_name_fa":
                "خانه اول",

            "sign":
                asc_position["sign"],

            "sign_fa":
                asc_position["sign_fa"],
        }


    # =====================================================
    # MC
    # =====================================================

    mc = (
        angles.get("mc")
        or angles.get("MC")
        or angles.get("midheaven")
    )

    mc_lon = None

    if isinstance(
        mc,
        dict
    ):
        mc_lon = _extract_longitude(
            mc
        )

    elif mc is not None:

        try:
            mc_lon = float(
                mc
            )

        except (
            TypeError,
            ValueError,
        ):
            mc_lon = None


    if mc_lon is not None:

        mc_position = _format_position(
            mc_lon
        )

        targets["MC"] = {
            "longitude":
                mc_position["longitude"],

            "target_type":
                "angle",

            "house":
                10,

            "house_name_fa":
                "خانه دهم",

            "sign":
                mc_position["sign"],

            "sign_fa":
                mc_position["sign_fa"],
        }


    # =====================================================
    # FALLBACK:
    # بعضی نسخه‌های natal.py ممکن است ASC/MC را بیرون
    # از angles قرار داده باشند.
    # =====================================================

    if "ASC" not in targets:

        for key in (
            "ascendant",
            "ASC",
            "asc",
        ):

            value = natal_chart.get(
                key
            )

            lon = _extract_longitude(
                value
            )

            if lon is not None:

                position = _format_position(
                    lon
                )

                targets["ASC"] = {
                    "longitude":
                        position["longitude"],

                    "target_type":
                        "angle",

                    "house":
                        1,

                    "house_name_fa":
                        "خانه اول",

                    "sign":
                        position["sign"],

                    "sign_fa":
                        position["sign_fa"],
                }

                break


    if "MC" not in targets:

        for key in (
            "mc",
            "MC",
            "midheaven",
        ):

            value = natal_chart.get(
                key
            )

            lon = _extract_longitude(
                value
            )

            if lon is not None:

                position = _format_position(
                    lon
                )

                targets["MC"] = {
                    "longitude":
                        position["longitude"],

                    "target_type":
                        "angle",

                    "house":
                        10,

                    "house_name_fa":
                        "خانه دهم",

                    "sign":
                        position["sign"],

                    "sign_fa":
                        position["sign_fa"],
                }

                break


    return targets


# =========================================================
# TRANSIT → NATAL
# =========================================================

def _calculate_natal_transits(
    transit_positions: dict,
    natal_chart: dict
):

    results = []

    if not isinstance(
        transit_positions,
        dict
    ):
        print(
            "NATAL TRANSIT ERROR: "
            "Invalid transit positions."
        )
        return results

    if not isinstance(
        natal_chart,
        dict
    ):
        print(
            "NATAL TRANSIT ERROR: "
            "Invalid natal chart."
        )
        return results


    # =====================================================
    # استخراج نقاط تولد
    # =====================================================

    natal_targets = _extract_natal_targets(
        natal_chart
    )

    print(
        "NATAL TARGETS:",
        list(
            natal_targets.keys()
        )
    )

    if not natal_targets:

        print(
            "NATAL TRANSIT ERROR: "
            "No natal targets found."
        )

        return results


    # =====================================================
    # بررسی Transit ها
    # =====================================================

    print(
        "TRANSIT PLANETS:",
        list(
            transit_positions.keys()
        )
    )


    # =====================================================
    # Transit → Natal
    # =====================================================

    for (
        transit_name,
        transit_data
    ) in transit_positions.items():

        if not isinstance(
            transit_data,
            dict
        ):
            continue

        transit_lon = _extract_longitude(
            transit_data
        )

        if transit_lon is None:
            continue


        for (
            natal_name,
            natal_data
        ) in natal_targets.items():

            if not isinstance(
                natal_data,
                dict
            ):
                continue

            natal_lon = _extract_longitude(
                natal_data
            )

            if natal_lon is None:
                continue


            # =================================================
            # فاصله زاویه‌ای واقعی
            # =================================================

            diff = _degree_difference(
                transit_lon,
                natal_lon
            )

            aspect = _find_aspect(
                diff
            )

            if aspect is None:
                continue


            # =================================================
            # Importance
            # =================================================

            importance = int(
                aspect["weight"]
            )


            # نقاط مهم تولد
            if natal_name in {
                "Sun",
                "Moon",
                "ASC",
                "MC",
            }:

                importance += 2


            # سیارات بیرونی
            if transit_name in {
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            }:

                importance += 1


            # =================================================
            # اطلاعات تولد
            # =================================================

            natal_fa = PLANET_FA.get(
                natal_name,
                natal_name
            )

            house = natal_data.get(
                "house"
            )

            house_name_fa = (
                natal_data.get(
                    "house_name_fa"
                )
            )

            if (
                not house_name_fa
                and house is not None
            ):

                try:

                    house_name_fa = (
                        f"خانه "
                        f"{int(house)}"
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    house_name_fa = str(
                        house
                    )


            # =================================================
            # Result
            # =================================================

            item = {

                # -----------------------------
                # Transit
                # -----------------------------

                "transit_planet":
                    transit_name,

                "transit_planet_fa":
                    PLANET_FA.get(
                        transit_name,
                        transit_name
                    ),

                "transit_symbol":
                    PLANET_SYMBOL.get(
                        transit_name,
                        ""
                    ),


                # -----------------------------
                # Natal
                # -----------------------------

                "natal_target":
                    natal_name,

                "natal_target_fa":
                    natal_fa,

                "natal_planet":
                    natal_name,

                "natal_planet_fa":
                    natal_fa,

                "natal_symbol":
                    PLANET_SYMBOL.get(
                        natal_name,
                        ""
                    ),

                "target_type":
                    natal_data.get(
                        "target_type",
                        "planet"
                    ),


                # -----------------------------
                # Aspect
                # -----------------------------

                "aspect":
                    aspect["aspect"],

                "aspect_fa":
                    aspect["aspect_fa"],

                "aspect_symbol":
                    aspect["aspect_symbol"],

                "aspect_degree":
                    aspect["aspect_degree"],

                "exact_diff":
                    round(
                        diff,
                        4
                    ),

                "orb":
                    round(
                        aspect["orb"],
                        4
                    ),

                "importance":
                    importance,


                # -----------------------------
                # Transit position
                # -----------------------------

                "transit_longitude":
                    round(
                        transit_lon,
                        6
                    ),

                "transit_position":
                    transit_data.get(
                        "formatted",
                        ""
                    ),

                "transit_sign":
                    transit_data.get(
                        "sign"
                    ),

                "transit_sign_fa":
                    transit_data.get(
                        "sign_fa"
                    ),

                "transit_retrograde":
                    transit_data.get(
                        "retrograde",
                        False
                    ),


                # -----------------------------
                # Natal position
                # -----------------------------

                "natal_longitude":
                    round(
                        natal_lon,
                        6
                    ),

                "natal_sign":
                    natal_data.get(
                        "sign"
                    ),

                "natal_sign_fa":
                    natal_data.get(
                        "sign_fa"
                    ),

                "natal_house":
                    house,

                "natal_house_name_fa":
                    house_name_fa,
            }


            results.append(
                item
            )


    # =====================================================
    # مرتب‌سازی
    # =====================================================

    results.sort(
        key=lambda x: (
            -x["importance"],
            x["orb"]
        )
    )


    print(
        "NATAL TRANSITS FOUND:",
        len(results)
    )


    # =====================================================
    # نمایش چند نتیجه اول در لاگ
    # =====================================================

    for item in results[:10]:

        print(
            "NATAL TRANSIT:",
            item["transit_planet"],
            "→",
            item["natal_target"],
            "|",
            item["aspect"],
            "| orb:",
            item["orb"]
        )


    return results


# =========================================================
# INTERPRETATION
# =========================================================

def _interpret_natal_transit(
    item: dict
):

    transit = item.get(
        "transit_planet_fa",
        item.get(
            "transit_planet",
            ""
        )
    )

    natal = item.get(
        "natal_target_fa",
        item.get(
            "natal_target",
            ""
        )
    )

    aspect = item.get(
        "aspect_fa",
        ""
    )

    if item.get(
        "aspect"
    ) == "trine":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ این الگو از نظر "
            f"تفسیری می‌تواند نشان‌دهنده "
            f"هماهنگی و جریان روان‌تر "
            f"انرژی میان این دو نقطه باشد."
        )


    if item.get(
        "aspect"
    ) == "sextile":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ این الگو می‌تواند "
            f"فرصتی برای استفاده آگاهانه "
            f"از انرژی این بخش از چارت ایجاد کند."
        )


    if item.get(
        "aspect"
    ) == "square":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ این الگو معمولاً "
            f"به فشار، اصطکاک یا نیاز "
            f"به سازگاری اشاره می‌کند."
        )


    if item.get(
        "aspect"
    ) == "opposition":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ ممکن است یک محور "
            f"دوگانه یا کشمکش میان دو حوزه "
            f"زندگی را برجسته کند."
        )


    if item.get(
        "aspect"
    ) == "conjunction":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ بنابراین این بخش "
            f"از چارت می‌تواند در دوره فعلی "
            f"برجسته‌تر از حالت معمول باشد."
        )


    if item.get(
        "aspect"
    ) == "quincunx":

        return (
            f"ترانزیت {transit} با "
            f"{natal} در وضعیت {aspect} "
            f"قرار دارد؛ این الگو بیشتر "
            f"نیازمند تنظیم، اصلاح یا "
            f"تغییر زاویه نگاه است."
        )


    return (
        f"ترانزیت {transit} و "
        f"{natal} نیازمند توجه بیشتر است."
    )


# =========================================================
# FULL TRANSIT ANALYSIS
# =========================================================

def get_full_transit_analysis(
    natal_chart: dict | None = None
):

    now = datetime.now(
        timezone.utc
    )

    jd = _to_julian_day(
        now
    )


    # =====================================================
    # Current sky
    # =====================================================

    positions = _calculate_positions(
        jd
    )


    # =====================================================
    # Transit → Transit
    # =====================================================

    transit_aspects = (
        _calculate_transit_aspects(
            positions
        )
    )


    natal_transits = []


    # =====================================================
    # Natal chart
    # =====================================================

    if natal_chart is None:

        try:

            import natal

            natal_chart = (
                natal.get_natal_chart()
            )

        except Exception as exc:

            print(
                "Unable to load natal chart:",
                repr(exc),
            )

            natal_chart = None


    # =====================================================
    # Transit → Natal
    # =====================================================

    if natal_chart is not None:

        try:

            natal_transits = (
                _calculate_natal_transits(
                    positions,
                    natal_chart,
                )
            )


            # =================================================
            # Interpretation
            # =================================================

            for item in natal_transits:

                item[
                    "interpretation"
                ] = _interpret_natal_transit(
                    item
                )


        except Exception as exc:

            print(
                "Natal transit error:",
                repr(exc),
            )

            natal_transits = []


    # =====================================================
    # API
    # =====================================================

    return {

        "status":
            "ok",

        "generated_at":
            now.isoformat(),


        # -------------------------------------------------
        # Legacy
        # -------------------------------------------------

        "positions":
            positions,

        "transits":
            transit_aspects,


        # -------------------------------------------------
        # Frontend
        # -------------------------------------------------

        "current_positions":
            positions,

        "transit_aspects":
            transit_aspects,

        "natal_transits":
            natal_transits,


        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        "summary": {

            "planet_count":
                len(
                    positions
                ),

            "transit_aspect_count":
                len(
                    transit_aspects
                ),

            "natal_transit_count":
                len(
                    natal_transits
                ),

            "important_natal_transits":
                len(
                    [
                        x
                        for x in natal_transits
                        if x.get(
                            "importance",
                            0
                        ) >= 6
                    ]
                ),
        },
    }


# =========================================================
# PUBLIC API
# =========================================================

def get_today_transits():

    return get_full_transit_analysis()


def detect_aspects(
    natal_chart: dict | None = None
):

    data = get_full_transit_analysis(
        natal_chart
    )

    return data.get(
        "natal_transits",
        []
    )
