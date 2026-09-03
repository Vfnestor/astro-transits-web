from ephemeris import get_full_transit_analysis


# =========================================================
# ASTRO VAHID — PERSONAL ASTROLOGY ADVISOR
# Version 2.0
# =========================================================


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

    "ASC":
        "هویت بیرونی، رفتار و نحوه مواجهه با جهان",

    "MC":
        "مسیر شغلی، جایگاه اجتماعی و اهداف بلندمدت",
}


# =========================================================
# تفسیر آسپکت
# =========================================================

def _aspect_meaning(aspect):

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
# محاسبه اهمیت
# =========================================================

def _importance(item):

    transit = item.get(
        "transit_planet"
    )

    natal = item.get(
        "natal_target"
    )

    aspect = item.get(
        "aspect"
    )

    orb = float(
        item.get("orb", 99)
    )

    score = 0

    # سیارات کندتر اهمیت بیشتری دارند
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

    # نقاط مهم چارت تولد
    if natal in [
        "Sun",
        "Moon",
        "North Node",
        "South Node",
        "ASC",
        "MC",
    ]:
        score += 3

    else:
        score += 1

    # آسپکت‌های قوی
    if aspect in [
        "conjunction",
        "opposition",
        "square",
    ]:
        score += 2

    elif aspect in [
        "trine",
        "sextile",
    ]:
        score += 1

    # نزدیکی اورب
    if orb <= 0.5:
        score += 4

    elif orb <= 1:
        score += 3

    elif orb <= 2:
        score += 2

    elif orb <= 3:
        score += 1

    # اهمیت موجود در موتور اصلی
    score += int(
        item.get(
            "importance",
            0
        )
    )

    return score


# =========================================================
# تشخیص نوع سؤال
# =========================================================

def _question_type(question):

    text = question.lower()

    decision_words = [
        "تصمیم",
        "انتخاب",
        "انتخاب کنم",
        "دوراهی",
        "دو راه",
        "مردد",
        "مرددم",
        "تصمیم بگیرم",
        "تصمیم بگیرم یا",
    ]

    delay_words = [
        "صبر",
        "تعلل",
        "صبر کنم",
        "عجله",
        "سریع",
        "فوری",
        "الان",
    ]

    for word in decision_words:

        if word in text:
            return "decision"

    for word in delay_words:

        if word in text:
            return "decision"

    return "general"


# =========================================================
# تحلیل تصمیم‌گیری
# =========================================================

def _decision_guidance(aspects):

    action_score = 0
    caution_score = 0

    evidence = []

    for item in aspects[:12]:

        transit = item.get(
            "transit_planet"
        )

        aspect = item.get(
            "aspect"
        )

        orb = float(
            item.get(
                "orb",
                99
            )
        )

        natal = item.get(
            "natal_target"
        )

        importance = _importance(
            item
        )

        # -------------------------------------------------
        # انرژی اقدام
        # -------------------------------------------------

        if transit == "Mars":

            if aspect in [
                "conjunction",
                "trine",
                "sextile",
            ]:

                action_score += importance

                evidence.append(
                    "مریخ در وضعیت نسبتاً حمایتی "
                    "قرار دارد و انرژی اقدام را افزایش می‌دهد."
                )

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution_score += importance

                evidence.append(
                    "مریخ تحت فشار است و بهتر است "
                    "از واکنش عجولانه پرهیز شود."
                )

        # -------------------------------------------------
        # مشتری
        # -------------------------------------------------

        if transit == "Jupiter":

            if aspect in [
                "conjunction",
                "trine",
                "sextile",
            ]:

                action_score += importance

                evidence.append(
                    "مشتری نشانه‌ای از رشد و گسترش "
                    "فرصت‌ها نشان می‌دهد."
                )

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution_score += importance

                evidence.append(
                    "مشتری می‌تواند تمایل به "
                    "بزرگ‌نمایی یا تصمیم بیش از حد خوش‌بینانه ایجاد کند."
                )

        # -------------------------------------------------
        # زحل
        # -------------------------------------------------

        if transit == "Saturn":

            caution_score += importance

            evidence.append(
                "زحل بر احتیاط، مسئولیت و بررسی "
                "پیامدهای بلندمدت تأکید می‌کند."
            )

        # -------------------------------------------------
        # اورانوس
        # -------------------------------------------------

        if transit == "Uranus":

            if aspect in [
                "conjunction",
                "square",
                "opposition",
            ]:

                caution_score += importance

                evidence.append(
                    "اورانوس می‌تواند شرایط غیرقابل‌پیش‌بینی "
                    "یا تغییر ناگهانی ایجاد کند."
                )

        # -------------------------------------------------
        # نپتون
        # -------------------------------------------------

        if transit == "Neptune":

            caution_score += importance

            evidence.append(
                "نپتون می‌تواند وضوح تصمیم‌گیری را کاهش دهد؛ "
                "بررسی واقعیت‌ها اهمیت بیشتری پیدا می‌کند."
            )

        # -------------------------------------------------
        # عطارد
        # -------------------------------------------------

        if transit == "Mercury":

            if aspect in [
                "trine",
                "sextile",
            ]:

                action_score += importance

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution_score += importance

    # -----------------------------------------------------
    # نتیجه
    # -----------------------------------------------------

    if action_score > caution_score + 5:

        recommendation = (
            "کفه چارت فعلی بیشتر به سمت اقدام "
            "و تصمیم‌گیری متمایل است؛ البته نه تصمیم "
            "هیجانی و بدون بررسی."
        )

        direction = "action"

    elif caution_score > action_score + 5:

        recommendation = (
            "کفه چارت فعلی بیشتر به سمت مکث، "
            "بررسی اطلاعات و پرهیز از تصمیم عجولانه "
            "متمایل است."
        )

        direction = "delay"

    else:

        recommendation = (
            "چارت فعلی پیام کاملاً یک‌طرفه‌ای "
            "برای عجله یا تأخیر نمی‌دهد. بهتر است "
            "قبل از انتخاب، اطلاعات دو مسیر را "
            "مقایسه کنی و سپس تصمیم بگیری."
        )

        direction = "balanced"

    return {
        "direction":
            direction,

        "action_score":
            action_score,

        "caution_score":
            caution_score,

        "recommendation":
            recommendation,

        "evidence":
            evidence[:5],
    }


# =========================================================
# Advice
# =========================================================

def get_advice(question: str):

    question = (
        question or ""
    ).strip()

    if not question:

        return (
            "لطفاً سؤال خود را وارد کنید."
        )

    try:

        analysis = (
            get_full_transit_analysis()
        )

    except Exception as exc:

        print(
            "Advisor analysis error:",
            repr(exc),
        )

        return (
            "مشاور نتوانست اطلاعات نجومی "
            "فعلی را دریافت کند. لطفاً دوباره تلاش کنید."
        )

    aspects = analysis.get(
        "natal_transits",
        []
    )

    if not aspects:

        return (
            f"سؤال شما: «{question}»\n\n"
            "در محدوده اورب فعلی، "
            "جنبه ترانزیتی برجسته‌ای نسبت به "
            "چارت تولد پیدا نشد.\n\n"
            "بنابراین برای این تصمیم بهتر است "
            "فعلاً وزن بیشتری به شرایط واقعی، "
            "اطلاعات موجود و پیامدهای هر انتخاب بدهی."
        )

    ranked = sorted(
        aspects,
        key=_importance,
        reverse=True,
    )

    selected = ranked[:8]

    # =====================================================
    # سؤال تصمیم‌گیری
    # =====================================================

    if _question_type(question) == "decision":

        decision = _decision_guidance(
            selected
        )

        lines = []

        for item in selected[:6]:

            transit = item.get(
                "transit_planet_fa",
                item.get(
                    "transit_planet",
                    "نامشخص"
                ),
            )

            natal = item.get(
                "natal_planet_fa",
                item.get(
                    "natal_target_fa",
                    item.get(
                        "natal_target",
                        "نامشخص"
                    ),
                ),
            )

            aspect = item.get(
                "aspect_fa",
                item.get(
                    "aspect",
                    "نامشخص"
                ),
            )

            orb = item.get(
                "orb"
            )

            house = item.get(
                "natal_house_name_fa"
            )

            line = (
                f"• {transit} فعلی با "
                f"{natal} تولدی در وضعیت "
                f"{aspect}"
            )

            if orb is not None:

                line += (
                    f" با اورب "
                    f"{float(orb):.2f}°"
                )

            line += " قرار دارد."

            if house:

                line += (
                    f" این ترانزیت با "
                    f"{house} مرتبط است."
                )

            lines.append(
                line
            )

        if decision["direction"] == "action":

            final_advice = (
                "اگر بخواهم بین «تعلل» و "
                "«اقدام» یکی را انتخاب کنم، "
                "بر اساس این خوانش نجومی، "
                "اقدام آگاهانه گزینه مناسب‌تری است. "
                "اما قبل از اقدام یک بررسی کوتاه "
                "از ریسک‌ها و اطلاعات واقعی انجام بده."
            )

        elif decision["direction"] == "delay":

            final_advice = (
                "اگر بخواهم بین «تعلل» و "
                "«تصمیم سریع» یکی را انتخاب کنم، "
                "بر اساس این خوانش نجومی، "
                "مکث و بررسی بیشتر مناسب‌تر است. "
                "این مکث به معنی رها کردن تصمیم نیست؛ "
                "بلکه یعنی قبل از حرکت، اطلاعات ناقص "
                "را کامل کنی."
            )

        else:

            final_advice = (
                "در این لحظه چارت یک پاسخ کاملاً "
                "قطعی به نفع عجله یا تعلل نمی‌دهد. "
                "بهترین رویکرد این است که یک مهلت "
                "کوتاه و مشخص برای جمع‌آوری اطلاعات "
                "تعیین کنی و بعد تصمیم بگیری."
            )

        return (
            f"سؤال شما: «{question}»\n\n"

            "### 🔭 وضعیت فعلی\n"
            + "\n".join(lines)
            + "\n\n"

            "### 🧭 نظر مشاور\n"
            + final_advice
            + "\n\n"

            "### 📊 جهت کلی\n"
            f"تمایل به اقدام: "
            f"{decision['action_score']}\n"
            f"تمایل به احتیاط: "
            f"{decision['caution_score']}\n\n"

            "### ⚠️ نکته مهم\n"
            "این یک تفسیر نجومی و نمادین است؛ "
            "تصمیم نهایی را بر اساس واقعیت‌های "
            "زندگی، اطلاعات قابل بررسی و پیامدهای "
            "واقعی هر انتخاب بگیر."
        )

    # =====================================================
    # سؤال عمومی
    # =====================================================

    lines = []

    for item in selected:

        transit = item.get(
            "transit_planet_fa",
            item.get(
                "transit_planet",
                "نامشخص"
            ),
        )

        natal = item.get(
            "natal_planet_fa",
            item.get(
                "natal_target_fa",
                item.get(
                    "natal_target",
                    "نامشخص"
                ),
            ),
        )

        aspect = item.get(
            "aspect_fa",
            item.get(
                "aspect",
                "نامشخص"
            ),
        )

        house = item.get(
            "natal_house_name_fa"
        )

        meaning = _aspect_meaning(
            item.get(
                "aspect"
            )
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

        lines.append(
            line
        )

    strongest = selected[0]

    strongest_transit = strongest.get(
        "transit_planet_fa",
        strongest.get(
            "transit_planet",
            "نامشخص"
        ),
    )

    strongest_natal = strongest.get(
        "natal_planet_fa",
        strongest.get(
            "natal_target_fa",
            strongest.get(
                "natal_target",
                "نامشخص"
            ),
        ),
    )

    strongest_aspect = strongest.get(
        "aspect_fa",
        strongest.get(
            "aspect",
            "نامشخص"
        ),
    )

    conclusion = (
        f"مهم‌ترین نشانه فعلی مربوط به "
        f"{strongest_transit} و "
        f"{strongest_natal} در وضعیت "
        f"{strongest_aspect} است."
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
