from ephemeris import (
    get_full_transit_analysis,
)

from natal import (
    PLANET_NAMES_FA,
)


# =========================================================
# تفسیر سیارات
# =========================================================

PLANET_MEANINGS = {

    "Sun":
        "هویت، اراده، مسیر شخصی و احساس قدرت فردی",

    "Moon":
        "احساسات، امنیت روانی، خانواده و واکنش‌های ناخودآگاه",

    "Mercury":
        "فکر، ارتباط، تصمیم‌گیری و یادگیری",

    "Venus":
        "عشق، روابط، جذابیت، ارزش‌ها و مسائل مالی",

    "Mars":
        "انرژی، اقدام، رقابت، خشم و انگیزه",

    "Jupiter":
        "رشد، فرصت، توسعه، باورها و گسترش افق دید",

    "Saturn":
        "مسئولیت، محدودیت، آزمون، نظم و بلوغ",

    "Uranus":
        "تغییر ناگهانی، آزادی و شکستن الگوهای قدیمی",

    "Neptune":
        "شهود، خیال، ابهام و معنویت",

    "Pluto":
        "تحول عمیق، قدرت، پایان و شروع دوباره",

    "North Node":
        "مسیر رشد و جهت تکاملی",

    "South Node":
        "الگوهای آشنا و گذشته",
}


# =========================================================
# تفسیر آسپکت
# =========================================================

def _aspect_meaning(
    aspect
):

    meanings = {

        "conjunction":
            "انرژی دو عامل بسیار متمرکز و پررنگ می‌شود.",

        "opposition":
            "نیاز به ایجاد تعادل میان دو نیروی متفاوت وجود دارد.",

        "trine":
            "جریان نسبتاً روان و هماهنگی طبیعی ایجاد می‌شود.",

        "square":
            "تنش و فشار ایجاد می‌شود و معمولاً فرد را به تغییر وادار می‌کند.",

        "sextile":
            "فرصتی برای رشد وجود دارد، اما استفاده از آن نیازمند اقدام است.",

        "quincunx":
            "نیاز به سازگاری، تنظیم و تغییر زاویه نگاه وجود دارد.",
    }

    return meanings.get(
        aspect,
        "نیاز به توجه و بررسی بیشتر وجود دارد.",
    )


# =========================================================
# شدت
# =========================================================

def _importance(item):

    transit = item[
        "transit_planet"
    ]

    natal = item[
        "natal_planet"
    ]

    aspect = item[
        "aspect"
    ]

    score = 0

    if transit in [
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Jupiter",
    ]:
        score += 3
    else:
        score += 1

    if natal in [
        "Sun",
        "Moon",
        "North Node",
    ]:
        score += 3
    else:
        score += 1

    if aspect in [
        "conjunction",
        "opposition",
        "square",
    ]:
        score += 2

    if item["orb"] <= 1:
        score += 3
    elif item["orb"] <= 2:
        score += 2

    return score


# =========================================================
# Advice
# =========================================================

def get_advice(
    question: str,
):

    analysis = (
        get_full_transit_analysis()
    )

    aspects = analysis[
        "natal_transits"
    ]

    if not aspects:

        return (
            f"سؤال شما: «{question}»\n\n"
            "در محدوده اورب انتخاب‌شده، "
            "در حال حاضر جنبه ترانزیتی برجسته‌ای "
            "نسبت به چارت تولد پیدا نشد.\n\n"
            "بنابراین بهتر است تصمیم را بیشتر "
            "بر اساس شرایط واقعی زندگی و اطلاعات "
            "قابل سنجش بگیری."
        )

    ranked = sorted(
        aspects,
        key=_importance,
        reverse=True,
    )

    selected = ranked[:6]

    lines = []

    for item in selected:

        transit = item[
            "transit_planet_fa"
        ]

        natal = item[
            "natal_planet_fa"
        ]

        aspect = item[
            "aspect_fa"
        ]

        house = item.get(
            "natal_house_name_fa"
        )

        meaning = _aspect_meaning(
            item["aspect"]
        )

        line = (
            f"• {transit} فعلی با "
            f"{natal} تولدی در وضعیت "
            f"{aspect} قرار دارد. "
            f"{meaning}"
        )

        if house:

            line += (
                f" این موضوع با "
                f"{house} چارت تولد "
                f"ارتباط دارد."
            )

        lines.append(line)

    strongest = selected[0]

    conclusion = (
        f"مهم‌ترین نشانه فعلی مربوط به "
        f"{strongest['transit_planet_fa']} "
        f"و {strongest['natal_planet_fa']} "
        f"در وضعیت "
        f"{strongest['aspect_fa']} است."
    )

    return (
        f"سؤال شما: «{question}»\n\n"

        "### وضعیت فعلی\n"
        + "\n".join(lines)
        + "\n\n"

        "### جمع‌بندی\n"
        + conclusion
        + "\n\n"

        "این متن یک تفسیر نجومی است و "
        "نباید به‌عنوان پیش‌بینی قطعی یا "
        "جایگزین تصمیم‌گیری بر اساس واقعیت "
        "در نظر گرفته شود."
    )
# Deploy sync 2026-09-02
