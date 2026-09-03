document.addEventListener("DOMContentLoaded", () => {

    // =========================================================
    // GLOBAL STATE
    // =========================================================

    let advisorHistory = [];
    let isAdvisorBusy = false;


    // =========================================================
    // DOM
    // =========================================================

    const questionInput =
        document.getElementById("questionInput");

    const advisorBox =
        document.getElementById("advisorBox");


    // =========================================================
    // HELPERS
    // =========================================================

    function escapeHtml(value) {

        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function safeArray(value) {

        return Array.isArray(value)
            ? value
            : [];
    }


    function safeObject(value) {

        return value &&
               typeof value === "object"
            ? value
            : {};
    }


    function firstValue(obj, keys, fallback = "—") {

        obj = safeObject(obj);

        for (const key of keys) {

            if (
                obj[key] !== undefined &&
                obj[key] !== null &&
                obj[key] !== ""
            ) {

                return obj[key];
            }
        }

        return fallback;
    }


    function formatNumber(value, digits = 2) {

        const n = Number(value);

        if (!Number.isFinite(n)) {
            return "—";
        }

        return n.toFixed(digits);
    }


    function formatOrb(value) {

        const n = Number(value);

        if (!Number.isFinite(n)) {
            return "—";
        }

        return `${n.toFixed(2)}°`;
    }


    function formatPosition(item) {

        item = safeObject(item);

        if (item.formatted) {
            return item.formatted;
        }

        const sign =
            firstValue(
                item,
                ["sign_fa", "sign"],
                ""
            );

        const degree =
            firstValue(
                item,
                ["degree"],
                ""
            );

        const minute =
            firstValue(
                item,
                ["minute"],
                ""
            );

        const second =
            firstValue(
                item,
                ["second"],
                ""
            );

        if (sign) {

            let result = `${degree}°`;

            if (minute !== "") {
                result += ` ${minute}′`;
            }

            if (second !== "") {
                result += ` ${second}″`;
            }

            result += ` ${sign}`;

            return result;
        }

        if (item.longitude !== undefined) {

            return `${formatNumber(item.longitude, 2)}°`;
        }

        return "—";
    }


    function planetName(item) {

        return firstValue(
            item,
            [
                "name_fa",
                "planet_fa",
                "natal_planet_fa",
                "target_fa",
                "planet"
            ],
            "—"
        );
    }


    function planetSymbol(item) {

        return firstValue(
            item,
            ["symbol"],
            "🪐"
        );
    }


    function aspectName(item) {

        return firstValue(
            item,
            [
                "aspect_fa",
                "aspect_name_fa",
                "aspect",
                "name_fa"
            ],
            "—"
        );
    }


    function houseName(item) {

        return firstValue(
            item,
            [
                "house_name_fa",
                "natal_house_name_fa",
                "house_fa"
            ],
            ""
        );
    }


    function showError(elementId, message) {

        const el =
            document.getElementById(elementId);

        if (!el) {
            return;
        }

        el.innerHTML = `
            <div class="loading">
                ⚠️ ${escapeHtml(message)}
            </div>
        `;
    }


    function setLoading(elementId, message) {

        const el =
            document.getElementById(elementId);

        if (!el) {
            return;
        }

        el.innerHTML = `
            <div class="loading">
                ${escapeHtml(message)}
            </div>
        `;
    }


    // =========================================================
    // FETCH WITH TIMEOUT
    // =========================================================

    async function fetchJson(
        url,
        options = {},
        timeout = 30000
    ) {

        const controller =
            new AbortController();

        const timer =
            setTimeout(
                () => controller.abort(),
                timeout
            );

        try {

            const response =
                await fetch(
                    url,
                    {
                        ...options,
                        signal:
                            controller.signal
                    }
                );

            const text =
                await response.text();

            let data;

            try {

                data =
                    text
                        ? JSON.parse(text)
                        : {};

            } catch {

                throw new Error(
                    `پاسخ نامعتبر از ${url}`
                );
            }

            if (!response.ok) {

                throw new Error(
                    data.message ||
                    `خطای HTTP ${response.status}`
                );
            }

            return data;

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                throw new Error(
                    "زمان دریافت پاسخ به پایان رسید."
                );
            }

            throw error;

        } finally {

            clearTimeout(timer);
        }
    }


    // =========================================================
    // NATAL CHART
    // =========================================================

    async function loadNatal() {

        setLoading(
            "planetTable",
            "در حال محاسبه سیارات..."
        );

        setLoading(
            "houseTable",
            "در حال محاسبه خانه‌ها..."
        );

        setLoading(
            "natalAspectTable",
            "در حال محاسبه جنبه‌ها..."
        );


        try {

            const data =
                await fetchJson(
                    "/natal"
                );


            const natal =
                safeObject(
                    data.natal || data
                );


            renderNatalSummary(
                natal
            );


            renderPlanetTable(
                natal
            );


            renderHouseTable(
                natal
            );


            renderNatalAspectTable(
                natal
            );


        } catch (error) {

            console.error(
                "Natal error:",
                error
            );


            showError(
                "planetTable",
                `خطا در دریافت چارت تولد: ${error.message}`
            );

            showError(
                "houseTable",
                "اطلاعات خانه‌ها دریافت نشد."
            );

            showError(
                "natalAspectTable",
                "اطلاعات جنبه‌های تولد دریافت نشد."
            );
        }
    }


    function renderNatalSummary(natal) {

        const planets =
            safeArray(
                natal.planets ||
                natal.positions
            );


        const findPlanet =
            (names) =>
                planets.find(
                    p =>
                        names.includes(
                            String(
                                firstValue(
                                    p,
                                    [
                                        "planet",
                                        "name",
                                        "name_en"
                                    ],
                                    ""
                                )
                            ).toLowerCase()
                        )
                );


        let sun =
            findPlanet(
                ["sun", "خورشید"]
            );

        let moon =
            findPlanet(
                ["moon", "ماه"]
            );


        // fallback by common fields
        if (!sun) {

            sun =
                planets.find(
                    p =>
                        String(
                            planetName(p)
                        ).includes("خورشید")
                );
        }


        if (!moon) {

            moon =
                planets.find(
                    p =>
                        String(
                            planetName(p)
                        ).includes("ماه")
                );
        }


        const asc =
            firstValue(
                natal,
                [
                    "ascendant",
                    "asc",
                    "ASC"
                ],
                null
            );


        const mc =
            firstValue(
                natal,
                [
                    "mc",
                    "MC",
                    "midheaven"
                ],
                null
            );


        setText(
            "sunPosition",
            sun
                ? formatPosition(sun)
                : firstValue(
                    natal,
                    ["sun_position"],
                    "—"
                )
        );


        setText(
            "moonPosition",
            moon
                ? formatPosition(moon)
                : firstValue(
                    natal,
                    ["moon_position"],
                    "—"
                )
        );


        setText(
            "ascPosition",
            formatPosition(
                typeof asc === "object"
                    ? asc
                    : {
                        formatted: asc
                    }
            )
        );


        setText(
            "mcPosition",
            formatPosition(
                typeof mc === "object"
                    ? mc
                    : {
                        formatted: mc
                    }
            )
        );
    }


    function setText(id, value) {

        const el =
            document.getElementById(id);

        if (el) {
            el.textContent =
                value ?? "—";
        }
    }


    // =========================================================
    // PLANET TABLE
    // =========================================================

    function renderPlanetTable(natal) {

        const container =
            document.getElementById(
                "planetTable"
            );

        if (!container) {
            return;
        }


        let planets =
            safeArray(
                natal.planets ||
                natal.positions
            );


        if (!planets.length) {

            container.innerHTML = `
                <div class="loading">
                    اطلاعات سیارات پیدا نشد.
                </div>
            `;

            return;
        }


        container.innerHTML = `

            <table class="astro-table">

                <thead>

                    <tr>
                        <th>جرم</th>
                        <th>موقعیت</th>
                        <th>خانه</th>
                        <th>حرکت</th>
                    </tr>

                </thead>

                <tbody>

                    ${planets.map(
                        planet => {

                            const retrograde =
                                planet.retrograde
                                    ? "℞ پس‌رو"
                                    : "مستقیم";

                            const house =
                                houseName(
                                    planet
                                ) ||
                                firstValue(
                                    planet,
                                    [
                                        "house",
                                        "house_number"
                                    ],
                                    "—"
                                );

                            return `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            planetSymbol(planet)
                                        )}
                                        ${escapeHtml(
                                            planetName(planet)
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            formatPosition(planet)
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            house
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            retrograde
                                        )}
                                    </td>

                                </tr>
                            `;
                        }
                    ).join("")}

                </tbody>

            </table>
        `;
    }


    // =========================================================
    // HOUSES
    // =========================================================

    function renderHouseTable(natal) {

        const container =
            document.getElementById(
                "houseTable"
            );

        if (!container) {
            return;
        }


        let houses =
            safeArray(
                natal.houses
            );


        if (!houses.length) {

            container.innerHTML = `
                <div class="loading">
                    اطلاعات خانه‌ها پیدا نشد.
                </div>
            `;

            return;
        }


        container.innerHTML = `

            <table class="astro-table">

                <thead>

                    <tr>
                        <th>خانه</th>
                        <th>برج</th>
                        <th>درجه</th>
                    </tr>

                </thead>

                <tbody>

                    ${houses.map(
                        (house, index) => {

                            const number =
                                firstValue(
                                    house,
                                    [
                                        "house",
                                        "number",
                                        "index"
                                    ],
                                    index + 1
                                );

                            const sign =
                                firstValue(
                                    house,
                                    [
                                        "sign_fa",
                                        "sign",
                                        "name_fa"
                                    ],
                                    "—"
                                );

                            return `

                                <tr>

                                    <td>
                                        خانه ${escapeHtml(
                                            number
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            sign
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            formatPosition(
                                                house
                                            )
                                        )}
                                    </td>

                                </tr>
                            `;
                        }
                    ).join("")}

                </tbody>

            </table>
        `;
    }


    // =========================================================
    // NATAL ASPECTS
    // =========================================================

    function renderNatalAspectTable(natal) {

        const container =
            document.getElementById(
                "natalAspectTable"
            );

        if (!container) {
            return;
        }


        const aspects =
            safeArray(
                natal.aspects
            );


        if (!aspects.length) {

            container.innerHTML = `
                <div class="loading">
                    جنبه قابل توجهی پیدا نشد.
                </div>
            `;

            return;
        }


        container.innerHTML = `

            <table class="astro-table">

                <thead>

                    <tr>
                        <th>جرم اول</th>
                        <th>جنبه</th>
                        <th>جرم دوم</th>
                        <th>Orb</th>
                    </tr>

                </thead>

                <tbody>

                    ${aspects.map(
                        aspect => {

                            const first =
                                firstValue(
                                    aspect,
                                    [
                                        "planet1_fa",
                                        "planet_a_fa",
                                        "first_planet_fa",
                                        "planet1"
                                    ],
                                    "—"
                                );

                            const second =
                                firstValue(
                                    aspect,
                                    [
                                        "planet2_fa",
                                        "planet_b_fa",
                                        "second_planet_fa",
                                        "planet2"
                                    ],
                                    "—"
                                );

                            return `

                                <tr>

                                    <td>
                                        ${escapeHtml(first)}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            aspectName(aspect)
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(second)}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            formatOrb(
                                                aspect.orb
                                            )
                                        )}
                                    </td>

                                </tr>
                            `;
                        }
                    ).join("")}

                </tbody>

            </table>
        `;
    }


    // =========================================================
    // TRANSITS
    // =========================================================

    async function loadTransits() {

        setLoading(
            "transitPositions",
            "در حال محاسبه موقعیت سیارات..."
        );

        setLoading(
            "transitAspectTable",
            "در حال بررسی جنبه‌های فعلی..."
        );

        setLoading(
            "natalTransitTable",
            "در حال بررسی ارتباط ترانزیت‌ها با چارت تولد..."
        );


        try {

            const data =
                await fetchJson(
                    "/analysis"
                );


            const transits =
                safeObject(
                    data.transits ||
                    data
                );


            renderTransitPositions(
                firstValue(
                    transits,
                    [
                        "current_positions",
                        "positions"
                    ],
                    []
                )
            );


            renderTransitAspects(
                firstValue(
                    transits,
                    [
                        "transit_aspects",
                        "transits"
                    ],
                    []
                )
            );


            renderNatalTransits(
                transits.natal_transits
            );


        } catch (error) {

            console.error(
                "Transit error:",
                error
            );


            showError(
                "transitPositions",
                `خطا در دریافت آسمان فعلی: ${error.message}`
            );

            showError(
                "transitAspectTable",
                "اطلاعات جنبه‌های فعلی دریافت نشد."
            );

            showError(
                "natalTransitTable",
                "اطلاعات ترانزیت به چارت تولد دریافت نشد."
            );
        }
    }


    // =========================================================
    // TRANSIT POSITIONS
    // =========================================================

    function renderTransitPositions(
        positions
    ) {

        const container =
            document.getElementById(
                "transitPositions"
            );

        if (!container) {
            return;
        }


        positions =
            safeArray(positions);


        if (!positions.length) {

            container.innerHTML = `
                <div class="loading">
                    اطلاعات آسمان امروز دریافت نشد.
                </div>
            `;

            return;
        }


        container.innerHTML =
            positions.map(
                planet => {

                    const retro =
                        planet.retrograde
                            ? `
                                <div class="retro">
                                    ℞ حرکت پس‌رو
                                </div>
                              `
                            : "";


                    return `

                        <div class="transit-card">

                            <div class="transit-symbol">
                                ${escapeHtml(
                                    planetSymbol(planet)
                                )}
                            </div>

                            <div class="transit-name">
                                ${escapeHtml(
                                    planetName(planet)
                                )}
                            </div>

                            <div class="transit-position">
                                ${escapeHtml(
                                    formatPosition(planet)
                                )}
                            </div>

                            ${retro}

                        </div>
                    `;
                }
            ).join("");
    }


    // =========================================================
    // TRANSIT → TRANSIT ASPECTS
    // =========================================================

    function renderTransitAspects(
        aspects
    ) {

        const container =
            document.getElementById(
                "transitAspectTable"
            );

        if (!container) {
            return;
        }


        aspects =
            safeArray(aspects);


        if (!aspects.length) {

            container.innerHTML = `
                <div class="loading">
                    در حال حاضر جنبه قابل توجهی بین سیارات پیدا نشد.
                </div>
            `;

            return;
        }


        container.innerHTML = `

            <table class="astro-table">

                <thead>

                    <tr>
                        <th>سیاره اول</th>
                        <th>جنبه</th>
                        <th>سیاره دوم</th>
                        <th>Orb</th>
                    </tr>

                </thead>

                <tbody>

                    ${aspects.map(
                        aspect => {

                            const first =
                                firstValue(
                                    aspect,
                                    [
                                        "planet1_fa",
                                        "planet_a_fa",
                                        "first_planet_fa",
                                        "planet1"
                                    ],
                                    "—"
                                );

                            const second =
                                firstValue(
                                    aspect,
                                    [
                                        "planet2_fa",
                                        "planet_b_fa",
                                        "second_planet_fa",
                                        "planet2"
                                    ],
                                    "—"
                                );

                            return `

                                <tr>

                                    <td>
                                        ${escapeHtml(first)}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            aspectName(aspect)
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(second)}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            formatOrb(
                                                aspect.orb
                                            )
                                        )}
                                    </td>

                                </tr>
                            `;
                        }
                    ).join("")}

                </tbody>

            </table>
        `;
    }


    // =========================================================
    // TRANSIT → NATAL
    // =========================================================

    function renderNatalTransits(
        aspects
    ) {

        const container =
            document.getElementById(
                "natalTransitTable"
            );

        if (!container) {
            return;
        }


        aspects =
            safeArray(aspects);


        if (!aspects.length) {

            container.innerHTML = `
                <div class="loading">
                    ارتباط قابل توجهی بین ترانزیت‌ها و چارت تولد پیدا نشد.
                </div>
            `;

            return;
        }


        container.innerHTML = `

            <table class="astro-table">

                <thead>

                    <tr>
                        <th>ترانزیت</th>
                        <th>جنبه</th>
                        <th>جرم تولدی</th>
                        <th>خانه</th>
                        <th>Orb</th>
                        <th>اهمیت</th>
                    </tr>

                </thead>

                <tbody>

                    ${aspects.map(
                        item => {

                            const transit =
                                firstValue(
                                    item,
                                    [
                                        "transit_planet_fa",
                                        "planet_fa",
                                        "name_fa",
                                        "transit_planet"
                                    ],
                                    "—"
                                );


                            const natalPlanet =
                                firstValue(
                                    item,
                                    [
                                        "natal_planet_fa",
                                        "natal_target_fa",
                                        "target_fa",
                                        "natal_planet",
                                        "natal_target"
                                    ],
                                    "—"
                                );


                            const house =
                                firstValue(
                                    item,
                                    [
                                        "natal_house_name_fa",
                                        "house_name_fa",
                                        "house_fa"
                                    ],
                                    ""
                                ) ||
                                (
                                    item.natal_house !== undefined
                                        ? `خانه ${item.natal_house}`
                                        : "—"
                                );


                            const importance =
                                firstValue(
                                    item,
                                    [
                                        "importance",
                                        "score"
                                    ],
                                    "—"
                                );


                            return `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            transit
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            aspectName(item)
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            natalPlanet
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            house
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            formatOrb(
                                                item.orb
                                            )
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            importance
                                        )}
                                    </td>

                                </tr>
                            `;
                        }
                    ).join("")}

                </tbody>

            </table>
        `;
    }


    // =========================================================
    // LOAD EVERYTHING
    // =========================================================

    async function loadAll() {

        await loadNatal();

        await loadTransits();
    }


    // =========================================================
    // ADVISOR
    // =========================================================

    function formatAdvisorText(text) {

        let html =
            escapeHtml(text);


        html =
            html.replace(
                /^### (.+)$/gm,
                '<div class="advisor-heading">$1</div>'
            );


        html =
            html.replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );


        html =
            html.replace(
                /\n/g,
                "<br>"
            );


        return html;
    }


    function addAdvisorMessage(
        role,
        text
    ) {

        if (!advisorBox) {
            return;
        }


        const message =
            document.createElement(
                "div"
            );


        message.className =
            role === "user"
                ? "advisor-message user"
                : "advisor-message assistant";


        message.innerHTML = `

            <div class="advisor-message-label">

                ${
                    role === "user"
                        ? "👤 شما"
                        : "🔮 مشاور"
                }

            </div>

            <div class="advisor-message-content">

                ${formatAdvisorText(text)}

            </div>
        `;


        advisorBox.appendChild(
            message
        );


        advisorBox.scrollTop =
            advisorBox.scrollHeight;
    }


    function addAdvisorLoading() {

        if (!advisorBox) {
            return;
        }


        removeAdvisorLoading();


        const loading =
            document.createElement(
                "div"
            );


        loading.id =
            "advisorLoading";


        loading.className =
            "advisor-message assistant";


        loading.innerHTML = `

            <div class="advisor-message-label">
                🔮 مشاور
            </div>

            <div class="advisor-message-content advisor-thinking">
                در حال بررسی چارت تولد، آسمان فعلی و روند روزهای آینده...
            </div>

        `;


        advisorBox.appendChild(
            loading
        );


        advisorBox.scrollTop =
            advisorBox.scrollHeight;
    }


    function removeAdvisorLoading() {

        const loading =
            document.getElementById(
                "advisorLoading"
            );

        if (loading) {
            loading.remove();
        }
    }


    async function askAdvisor() {

        if (
            !questionInput ||
            !advisorBox
        ) {
            return;
        }


        if (isAdvisorBusy) {
            return;
        }


        const question =
            questionInput.value.trim();


        if (!question) {

            questionInput.focus();

            return;
        }


        isAdvisorBusy =
            true;


        addAdvisorMessage(
            "user",
            question
        );


        questionInput.value =
            "";


        addAdvisorLoading();


        try {

            const data =
                await fetchJson(
                    "/advisor",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({

                                question:
                                    question,

                                history:
                                    advisorHistory

                            })
                    },
                    60000
                );


            removeAdvisorLoading();


            if (
                data.status ===
                "error"
            ) {

                addAdvisorMessage(
                    "assistant",
                    data.message ||
                    "مشاور نتوانست پاسخ دهد."
                );

                return;
            }


            const message =
                data.message ||
                "پاسخی از مشاور دریافت نشد.";


            advisorHistory.push({

                role:
                    "user",

                content:
                    question
            });


            advisorHistory.push({

                role:
                    "assistant",

                content:
                    message
            });


            if (
                advisorHistory.length >
                12
            ) {

                advisorHistory =
                    advisorHistory.slice(
                        -12
                    );
            }


            addAdvisorMessage(
                "assistant",
                message
            );


        } catch (error) {

            removeAdvisorLoading();


            console.error(
                "Advisor error:",
                error
            );


            addAdvisorMessage(
                "assistant",
                `خطا در ارتباط با مشاور: ${error.message}`
            );


        } finally {

            isAdvisorBusy =
                false;
        }
    }


    // =========================================================
    // ENTER KEY
    // =========================================================

    if (questionInput) {

        questionInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    askAdvisor();
                }
            }
        );
    }


    // =========================================================
    // ADVISOR INITIAL UI
    // =========================================================

    if (advisorBox) {

        advisorBox.classList.add(
            "advisor-chat"
        );

        advisorBox.innerHTML = `

            <div class="advisor-welcome">

                🔮 <strong>
                    مشاور نجومی شخصی
                </strong>

                <div>
                    سؤال خودت را بپرس.
                    اگر برای تحلیل دقیق‌تر اطلاعات بیشتری لازم باشد،
                    مشاور ابتدا از تو سؤال می‌پرسد و سپس تحلیل را ادامه می‌دهد.
                </div>

            </div>
        `;
    }


    // =========================================================
    // EXPOSE GLOBAL FUNCTIONS
    // =========================================================
    // چون دکمه‌های index.html از onclick استفاده می‌کنند،
    // این توابع باید روی window باشند.

    window.loadAll =
        loadAll;

    window.loadNatal =
        loadNatal;

    window.loadTransits =
        loadTransits;

    window.askAdvisor =
        askAdvisor;


    // =========================================================
    // AUTO LOAD
    // =========================================================

    loadAll();

});
