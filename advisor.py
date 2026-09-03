from datetime import datetime, timedelta, timezone

from ephemeris import (
    get_full_transit_analysis,
    _calculate_positions,
    _calculate_natal_transits,
    _to_julian_day,
)


# =========================================================
# ASTRO VAHID — PERSONAL ASTROLOGY ADVISOR
# Version 3.0
# Interactive / Contextual / 7-Day Analysis
# =========================================================


PLANET_MEANINGS = {

    "Sun":
        "هویت، اراده و مسیر شخصی",

    "Moon":
        "احساسات، امنیت روانی و واکنش‌های ناخودآگاه",

    "Mercury":
        "فکر، ارتباط، تصمیم‌گیری و تحلیل",

    "Venus":
        "روابط، ارزش‌ها، جذابیت و مسائل مالی",

    "Mars":
        "انرژی، اقدام، رقابت و انگیزه",

    "Jupiter":
        "رشد، فرصت، توسعه و گسترش",

    "Saturn":
        "مسئولیت، محدودیت، نظم و بلوغ",

    "Uranus":
        "تغییر ناگهانی، آزادی و شکستن الگوهای قدیمی",

    "Neptune":
        "شهود، خیال، ابهام و برداشت ذهنی",

    "Pluto":
        "تحول عمیق، قدرت و تغییر بنیادی",

    "North Node":
        "مسیر رشد و جهت تکاملی",

    "South Node":
        "الگوهای آشنا و گذشته",

    "ASC":
        "هویت بیرونی و نحوه مواجهه با جهان",

    "MC":
        "مسیر شغلی، جایگاه اجتماعی و اهداف بلندمدت",
}


# =========================================================
# تشخیص موضوع سؤال
# =========================================================

def _detect_topic(question):

    text = question.lower()

    if any(
        word in text
        for word in [
            "طلا",
            "سرمایه",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "پول",
            "خرید",
            "فروش",
            "دلار",
            "ارز",
            "بورس",
            "کریپتو",
            "بیت کوین",
        ]
    ):
        return "finance"

    if any(
        word in text
        for word in [
            "کار",
            "شغل",
            "شغلی",
            "استخدام",
            "کسب و کار",
            "کسب‌وکار",
            "شرکت",
        ]
    ):
        return "career"

    if any(
        word in text
        for word in [
            "عشق",
            "رابطه",
            "ازدواج",
            "همسر",
            "دوست",
            "عاطفی",
        ]
    ):
        return "relationship"

    if any(
        word in text
        for word in [
            "تصمیم",
            "انتخاب",
            "مردد",
            "دوراهی",
            "دو راه",
            "تعلل",
            "صبر",
            "عجله",
        ]
    ):
        return "decision"

    return "general"


# =========================================================
# تشخیص نیاز به اطلاعات بیشتر
# =========================================================

def _needs_more_information(
    question,
    history,
):

    topic = _detect_topic(
        question
    )

    # اگر قبلاً سؤال تکمیلی پرسیده‌ایم
    if len(history) >= 2:
        return False

    if topic == "finance":

        # سؤال‌های خیلی کلی مالی
        if not any(
            word in question.lower()
            for word in [
                "کوتاه",
                "بلند",
                "یک هفته",
                "هفته",
                "ماه",
                "ماهانه",
                "چند ماه",
                "سرمایه",
                "مبلغ",
                "بخشی",
                "همه",
            ]
        ):
            return True

    if topic == "decision":

        if not any(
            word in question.lower()
            for word in [
                "امروز",
                "فردا",
                "هفته",
                "زمان",
                "راه اول",
                "راه دوم",
            ]
        ):
            return True

    return False


# =========================================================
# سؤال تکمیلی
# =========================================================

def _follow_up_question(
    question
):

    topic = _detect_topic(
        question
    )

    if topic == "finance":

        return (
            "برای اینکه تحلیل را دقیق‌تر کنم، "
            "سه نکته برایم مشخص کن:\n\n"
            "۱. افق سرمایه‌گذاری‌ات کوتاه‌مدت است "
            "یا چندماهه/بلندمدت؟\n\n"
            "۲. قصد داری تمام سرمایه را وارد کنی "
            "یا فقط بخشی از آن را؟\n\n"
            "۳. اگر در چند روز آینده شرایط مطابق "
            "انتظارت پیش نرفت، امکان صبر کردن داری؟"
        )

    if topic == "decision":

        return (
            "برای اینکه بین «اقدام» و «صبر» "
            "تفسیر دقیق‌تری بدهم، بگو:\n\n"
            "۱. این تصمیم مربوط به چه موضوعی است؟\n\n"
            "۲. آیا مهلت مشخصی برای تصمیم داری؟\n\n"
            "۳. اگر امروز تصمیم نگیری، چه چیزی ممکن "
            "است از دست برود؟"
        )

    return (
        "قبل از اینکه جمع‌بندی کنم، کمی بیشتر "
        "درباره شرایط واقعی این موضوع برایم بگو "
        "تا تحلیل را شخصی‌تر انجام دهم."
    )


# =========================================================
# تحلیل یک لحظه
# =========================================================

def _get_transits_for_datetime(
    natal_chart,
    dt
):

    jd = _to_julian_day(
        dt
    )

    positions = _calculate_positions(
        jd
    )

    natal_transits = (
        _calculate_natal_transits(
            positions,
            natal_chart
        )
    )

    return {
        "positions":
            positions,

        "natal_transits":
            natal_transits,
    }


# =========================================================
# تحلیل روند ۷ روز
# =========================================================

def _analyze_week(
    natal_chart
):

    now = datetime.now(
        timezone.utc
    )

    samples = []

    for day in range(8):

        dt = now + timedelta(
            days=day
        )

        data = _get_transits_for_datetime(
            natal_chart,
            dt
        )

        important = sorted(
            data["natal_transits"],
            key=lambda item: (
                -int(
                    item.get(
                        "importance",
                        0
                    )
                ),
                float(
                    item.get(
                        "orb",
                        99
                    )
                ),
            )
        )[:5]

        samples.append(
            {
                "day": day,
                "date": dt.date().isoformat(),
                "aspects": important,
            }
        )

    return samples


# =========================================================
# تشخیص روند یک ترانزیت
# =========================================================

def _trend(
    today_item,
    future_item
):

    if not today_item or not future_item:
        return "نامشخص"

    today_orb = float(
        today_item.get(
            "orb",
            99
        )
    )

    future_orb = float(
        future_item.get(
            "orb",
            99
        )
    )

    if future_orb < today_orb - 0.15:
        return "در حال نزدیک شدن"

    if future_orb > today_orb + 0.15:
        return "در حال جدا شدن"

    return "تقریباً ثابت"


# =========================================================
# اهمیت
# =========================================================

def _importance(item):

    score = int(
        item.get(
            "importance",
            0
        )
    )

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
        item.get(
            "orb",
            99
        )
    )

    if transit in [
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]:
        score += 3

    if natal in [
        "Sun",
        "Moon",
        "ASC",
        "MC",
        "North Node",
        "South Node",
    ]:
        score += 3

    if aspect in [
        "conjunction",
        "opposition",
        "square",
    ]:
        score += 2

    if orb <= 0.5:
        score += 4

    elif orb <= 1:
        score += 3

    elif orb <= 2:
        score += 2

    elif orb <= 3:
        score += 1

    return score


# =========================================================
# تحلیل تصمیم
# =========================================================

def _decision_analysis(
    aspects
):

    action = 0
    caution = 0

    reasons = []

    for item in aspects:

        transit = item.get(
            "transit_planet"
        )

        aspect = item.get(
            "aspect"
        )

        score = _importance(
            item
        )

        # -----------------------------
        # Mars
        # -----------------------------

        if transit == "Mars":

            if aspect in [
                "conjunction",
                "trine",
                "sextile",
            ]:

                action += score

                reasons.append(
                    "مریخ از نظر نمادین انرژی "
                    "اقدام و حرکت را تقویت می‌کند."
                )

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution += score

                reasons.append(
                    "مریخ تحت فشار است و احتمال "
                    "واکنش عجولانه بیشتر می‌شود."
                )

        # -----------------------------
        # Jupiter
        # -----------------------------

        if transit == "Jupiter":

            if aspect in [
                "conjunction",
                "trine",
                "sextile",
            ]:

                action += score

                reasons.append(
                    "مشتری از نظر نمادین فضای "
                    "رشد و گسترش را تقویت می‌کند."
                )

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution += score

                reasons.append(
                    "مشتری می‌تواند باعث خوش‌بینی "
                    "بیش از اندازه شود."
                )

        # -----------------------------
        # Saturn
        # -----------------------------

        if transit == "Saturn":

            caution += score

            reasons.append(
                "زحل بر بررسی، مسئولیت و "
                "پیامدهای بلندمدت تأکید دارد."
            )

        # -----------------------------
        # Uranus
        # -----------------------------

        if transit == "Uranus":

            if aspect in [
                "square",
                "opposition",
                "conjunction",
            ]:

                caution += score

                reasons.append(
                    "اورانوس می‌تواند شرایط "
                    "غافلگیرکننده ایجاد کند."
                )

        # -----------------------------
        # Neptune
        # -----------------------------

        if transit == "Neptune":

            caution += score

            reasons.append(
                "نپتون می‌تواند وضوح تصمیم‌گیری "
                "را کاهش دهد."
            )

        # -----------------------------
        # Mercury
        # -----------------------------

        if transit == "Mercury":

            if aspect in [
                "trine",
                "sextile",
            ]:

                action += score

            elif aspect in [
                "square",
                "opposition",
            ]:

                caution += score

    if action > caution + 8:

        direction = "action"

    elif caution > action + 8:

        direction = "delay"

    else:

        direction = "balanced"

    return {
        "action":
            action,

        "caution":
            caution,

        "direction":
            direction,

        "reasons":
            list(
                dict.fromkeys(
                    reasons
                )
            )[:5],
    }


# =========================================================
# تحلیل مالی
# =========================================================

def _finance_analysis(
    question,
    natal_chart,
):

    today = _get_transits_for_datetime(
        natal_chart,
        datetime.now(
            timezone.utc
        )
    )

    week = _analyze_week(
        natal_chart
    )

    today_aspects = sorted(
        today["natal_transits"],
        key=_importance,
        reverse=True
    )

    decision = _decision_analysis(
        today_aspects[:15]
    )

    return {
        "today":
            today_aspects[:8],

        "week":
            week,

        "decision":
            decision,
    }


# =========================================================
# ساخت پاسخ
# =========================================================

def _build_finance_response(
    question,
    result,
):

    today = result[
        "today"
    ]

    decision = result[
        "decision"
    ]

    lines = []

    for item in today[:6]:

        transit = item.get(
            "transit_planet_fa",
            item.get(
                "transit_planet",
                "نامشخص"
            )
        )

        natal = item.get(
            "natal_planet_fa",
            item.get(
                "natal_target_fa",
                "نامشخص"
            )
        )

        aspect = item.get(
            "aspect_fa",
            item.get(
                "aspect",
                "نامشخص"
            )
        )

        orb = float(
            item.get(
                "orb",
                0
            )
        )

        house = item.get(
            "natal_house_name_fa"
        )

        text = (
            f"• {transit} فعلی با "
            f"{natal} تولدی در وضعیت "
            f"{aspect} قرار دارد "
            f"(Orb {orb:.2f}°)"
        )

        if house:
            text += (
                f" و با {house} مرتبط است."
            )

        else:
            text += "."

        lines.append(
            text
        )

    # -----------------------------------------------------
    # جهت تصمیم
    # -----------------------------------------------------

    if decision["direction"] == "action":

        conclusion = (
            "در خوانش نجومی امروز، کفه کمی "
            "به سمت اقدام متمایل است. با این حال "
            "این به معنی مناسب بودن ورود یک‌باره "
            "و بدون مدیریت ریسک نیست."
        )

    elif decision["direction"] == "delay":

        conclusion = (
            "در خوانش نجومی امروز، کفه بیشتر "
            "به سمت احتیاط و مکث متمایل است. "
            "بهتر است تصمیم عجولانه نگیری و "
            "اطلاعات بیشتری جمع کنی."
        )

    else:

        conclusion = (
            "خوانش امروز یک سیگنال کاملاً "
            "یک‌طرفه برای اقدام یا تأخیر نشان "
            "نمی‌دهد. بنابراین بهتر است تصمیم "
            "را مرحله‌ای و با مدیریت ریسک بگیری."
        )

    # -----------------------------------------------------
    # روند هفته
    # -----------------------------------------------------

    week_text = []

    for day in result["week"][1:]:

        if not day["aspects"]:
            continue

        strongest = day["aspects"][0]

        transit = strongest.get(
            "transit_planet_fa",
            strongest.get(
                "transit_planet",
                ""
            )
        )

        natal = strongest.get(
            "natal_planet_fa",
            strongest.get(
                "natal_target_fa",
                ""
            )
        )

        aspect = strongest.get(
            "aspect_fa",
            strongest.get(
                "aspect",
                ""
            )
        )

        orb = float(
            strongest.get(
                "orb",
                0
            )
        )

        week_text.append(
            f"• +{day['day']} روز: "
            f"{transit} با {natal} "
            f"{aspect} — Orb {orb:.2f}°"
        )

    return (
        f"سؤال شما: «{question}»\n\n"

        "### 🔭 تحلیل چارت امروز\n"
        + "\n".join(lines)
        + "\n\n"

        "### 📅 روند هفت روز آینده\n"
        + "\n".join(
            week_text[:7]
        )
        + "\n\n"

        "### 🧭 جمع‌بندی مشاور\n"
        + conclusion
        + "\n\n"

        "### 📊 وضعیت کلی\n"
        f"تمایل به اقدام: "
        f"{decision['action']}\n"
        f"تمایل به احتیاط: "
        f"{decision['caution']}\n\n"

        "### 🔎 نکته مهم\n"
        "در موضوعات مالی، این تحلیل صرفاً "
        "یک خوانش نجومی است و پیش‌بینی قطعی "
        "قیمت طلا یا توصیه مالی محسوب نمی‌شود. "
        "تصمیم نهایی را بر اساس قیمت، روند بازار، "
        "نقدینگی، ریسک و شرایط واقعی خودت بگیر."
    )


# =========================================================
# پاسخ عمومی
# =========================================================

def _build_general_response(
    question,
    aspects,
):

    lines = []

    for item in aspects[:7]:

        transit = item.get(
            "transit_planet_fa",
            item.get(
                "transit_planet",
                ""
            )
        )

        natal = item.get(
            "natal_planet_fa",
            item.get(
                "natal_target_fa",
                ""
            )
        )

        aspect = item.get(
            "aspect_fa",
            item.get(
                "aspect",
                ""
            )
        )

        orb = float(
            item.get(
                "orb",
                0
            )
        )

        lines.append(
            f"• {transit} با {natal} "
            f"در وضعیت {aspect} "
            f"(Orb {orb:.2f}°)"
        )

    strongest = aspects[0]

    return (
        f"سؤال شما: «{question}»\n\n"

        "### 🔭 مهم‌ترین نشانه‌های فعلی\n"
        + "\n".join(lines)
        + "\n\n"

        "### 🧭 برداشت مشاور\n"
        f"قوی‌ترین نشانه فعلی مربوط به "
        f"{strongest.get('transit_planet_fa', '')} "
        f"و {strongest.get('natal_planet_fa', '')} "
        f"در وضعیت "
        f"{strongest.get('aspect_fa', '')} است.\n\n"

        "این تفسیر نجومی جنبه نمادین دارد و "
        "پیش‌بینی قطعی آینده نیست."
    )


# =========================================================
# MAIN ADVISOR
# =========================================================

def get_advice(
    question: str,
    history=None,
):

    question = (
        question or ""
    ).strip()

    history = history or []

    if not question:

        return {
            "status": "error",
            "message":
                "لطفاً سؤال خود را وارد کنید.",
        }

    try:

        analysis = (
            get_full_transit_analysis()
        )

        natal_chart = None

        try:
            import natal

            natal_chart = (
                natal.get_natal_chart()
            )

        except Exception as exc:

            print(
                "Natal loading error:",
                repr(exc)
            )

        # =================================================
        # سؤال تکمیلی
        # =================================================

        if _needs_more_information(
            question,
            history
        ):

            return {
                "status":
                    "follow_up",

                "question":
                    question,

                "topic":
                    _detect_topic(
                        question
                    ),

                "message":
                    _follow_up_question(
                        question
                    ),

                "analysis_ready":
                    False,
            }

        aspects = sorted(
            analysis.get(
                "natal_transits",
                []
            ),
            key=_importance,
            reverse=True,
        )

        topic = _detect_topic(
            question
        )

        # =================================================
        # مالی
        # =================================================

        if (
            topic == "finance"
            and natal_chart is not None
        ):

            finance = _finance_analysis(
                question,
                natal_chart
            )

            response = _build_finance_response(
                question,
                finance
            )

        # =================================================
        # تصمیم‌گیری
        # =================================================

        elif topic == "decision":

            decision = _decision_analysis(
                aspects[:15]
            )

            if decision["direction"] == "action":

                conclusion = (
                    "کفه فعلی بیشتر به سمت "
                    "اقدام آگاهانه متمایل است؛ "
                    "اما نه تصمیم هیجانی."
                )

            elif decision["direction"] == "delay":

                conclusion = (
                    "کفه فعلی بیشتر به سمت "
                    "مکث و بررسی بیشتر متمایل است."
                )

            else:

                conclusion = (
                    "سیگنال فعلی کاملاً یک‌طرفه "
                    "نیست؛ بهتر است تصمیم را "
                    "مرحله‌ای بگیری."
                )

            response = (
                f"سؤال شما: «{question}»\n\n"

                "### 🔭 تحلیل\n"
                + "\n".join(
                    [
                        f"• {x.get('transit_planet_fa', '')} "
                        f"با {x.get('natal_planet_fa', '')} "
                        f"{x.get('aspect_fa', '')} "
                        f"(Orb {float(x.get('orb', 0)):.2f}°)"
                        for x in aspects[:7]
                    ]
                )
                + "\n\n"

                "### 🧭 نظر مشاور\n"
                + conclusion
                + "\n\n"

                "این برداشت بر اساس تفسیر نجومی "
                "است و تصمیم نهایی باید با توجه "
                "به شرایط واقعی گرفته شود."
            )

        # =================================================
        # عمومی
        # =================================================

        else:

            response = _build_general_response(
                question,
                aspects
            )

        return {
            "status":
                "ok",

            "question":
                question,

            "topic":
                topic,

            "message":
                response,

            "analysis_ready":
                True,
        }

    except Exception as exc:

        import traceback

        print(
            "ADVISOR ERROR:",
            repr(exc)
        )

        print(
            traceback.format_exc()
        )

        return {
            "status":
                "error",

            "message":
                "خطایی در تحلیل مشاور رخ داد.",

            "debug":
                str(exc),
        }
