/* =========================================================
   ASTRO TRANSITS WEB
   Frontend Controller
   Compatible with current /natal and /analysis API
   ========================================================= */

"use strict";

/* ---------------------------------------------------------
   Global state
--------------------------------------------------------- */

let natalData = null;
let analysisData = null;

let advisorHistory = [];


/* ---------------------------------------------------------
   Generic helpers
--------------------------------------------------------- */

function $(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const el = $(id);
    if (el) {
        el.textContent =
            value === undefined ||
            value === null ||
            value === ""
                ? "—"
                : String(value);
    }
}

function escapeHtml(value) {
    if (value === undefined || value === null) return "";

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function safeObject(value) {
    return value && typeof value === "object" && !Array.isArray(value)
        ? value
        : {};
}

function safeArray(value) {
    return Array.isArray(value) ? value : [];
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

function showLoading(id, text = "در حال دریافت اطلاعات...") {
    const el = $(id);

    if (el) {
        el.innerHTML = `
            <div class="loading-state">
                ${escapeHtml(text)}
            </div>
        `;
    }
}

function showError(id, text) {
    const el = $(id);

    if (el) {
        el.innerHTML = `
            <div class="error-state">
                ${escapeHtml(text)}
            </div>
        `;
    }
}


/* ---------------------------------------------------------
   Fetch
--------------------------------------------------------- */

async function fetchJson(url, options = {}) {
    const controller = new AbortController();

    const timeout = setTimeout(() => {
        controller.abort();
    }, options.timeout || 30000);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
            headers: {
                "Accept": "application/json",
                ...(options.headers || {})
            }
        });

        const text = await response.text();

        let data;

        try {
            data = text ? JSON.parse(text) : {};
        } catch (e) {
            throw new Error("پاسخ سرور JSON معتبر نیست.");
        }

        if (!response.ok) {
            throw new Error(
                data?.message ||
                data?.detail ||
                `خطای سرور: ${response.status}`
            );
        }

        return data;

    } catch (error) {

        if (error.name === "AbortError") {
            throw new Error("زمان دریافت اطلاعات به پایان رسید.");
        }

        throw error;

    } finally {
        clearTimeout(timeout);
    }
}


/* =========================================================
   NATAL CHART
   ========================================================= */

async function loadNatal() {

    showLoading("planetTable", "در حال دریافت سیارات...");
    showLoading("houseTable", "در حال دریافت خانه‌ها...");
    showLoading("natalAspectTable", "در حال دریافت جنبه‌ها...");

    try {

        const data = await fetchJson("/natal");

        natalData = data;

        renderNatal(data);

    } catch (error) {

        console.error("Natal error:", error);

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
            "اطلاعات جنبه‌ها دریافت نشد."
        );
    }
}


/* ---------------------------------------------------------
   Render natal
--------------------------------------------------------- */

function renderNatal(data) {

    const birth = safeObject(data.birth_data);
    const angles = safeObject(data.angles);

    const asc = safeObject(angles.ascendant);
    const mc = safeObject(angles.mc);

    /*
       Summary
    */

    const dateFa = birth.date_fa || "—";
    const timeFa = birth.time_fa || "—";

    if ($("natalSummary")) {
        $("natalSummary").innerHTML = `
            <div>
                <strong>تاریخ تولد:</strong>
                ${escapeHtml(dateFa)}
            </div>

            <div>
                <strong>ساعت:</strong>
                ${escapeHtml(timeFa)}
            </div>

            <div>
                <strong>زودیاک:</strong>
                ${escapeHtml(data?.zodiac?.name_fa || "تروپیکال")}
            </div>

            <div>
                <strong>خانه‌ها:</strong>
                ${escapeHtml(data?.house_system?.name_fa || "پلاسیدوس")}
            </div>
        `;
    }

    /*
       Main angles
    */

    setText(
        "sunPosition",
        data?.planets?.Sun?.formatted || "—"
    );

    setText(
        "moonPosition",
        data?.planets?.Moon?.formatted || "—"
    );

    setText(
        "ascPosition",
        asc.formatted || "—"
    );

    setText(
        "mcPosition",
        mc.formatted || "—"
    );

    /*
       Planets
    */

    renderPlanetTable(data);

    /*
       Houses
    */

    renderHouseTable(data);

    /*
       Natal aspects
    */

    renderNatalAspects(data);
}


/* ---------------------------------------------------------
   Planet table
--------------------------------------------------------- */

function renderPlanetTable(data) {

    const container = $("planetTable");

    if (!container) return;

    const planets = safeObject(data.planets);
    const nodes = safeObject(data.nodes);

    const allObjects = [
        ...Object.entries(planets),
        ...Object.entries(nodes)
    ];

    if (!allObjects.length) {
        container.innerHTML = `
            <div class="empty-state">
                اطلاعات سیارات پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <div class="table-wrapper">
        <table class="astro-table">
            <thead>
                <tr>
                    <th>جرم</th>
                    <th>موقعیت</th>
                    <th>خانه</th>
                    <th>وضعیت</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [key, planet] of allObjects) {

        const name =
            planet.name_fa ||
            key;

        const position =
            planet.formatted ||
            "—";

        const house =
            planet.house_name_fa ||
            (planet.house
                ? `خانه ${planet.house}`
                : "—");

        const retrograde =
            planet.retrograde
                ? "رجعتی"
                : "مستقیم";

        html += `
            <tr>
                <td>
                    <strong>
                        ${escapeHtml(planet.symbol || "")}
                        ${escapeHtml(name)}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(position)}
                </td>

                <td>
                    ${escapeHtml(house)}
                </td>

                <td>
                    ${escapeHtml(retrograde)}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* ---------------------------------------------------------
   Houses
--------------------------------------------------------- */

function renderHouseTable(data) {

    const container = $("houseTable");

    if (!container) return;

    const houses = safeObject(data.houses);

    const entries = Object.entries(houses)
        .sort((a, b) => Number(a[0]) - Number(b[0]));

    if (!entries.length) {

        container.innerHTML = `
            <div class="empty-state">
                اطلاعات خانه‌ها پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <div class="table-wrapper">
        <table class="astro-table">
            <thead>
                <tr>
                    <th>خانه</th>
                    <th>برج</th>
                    <th>درجه</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [number, house] of entries) {

        html += `
            <tr>
                <td>
                    <strong>
                        ${escapeHtml(
                            house.name_fa ||
                            `خانه ${number}`
                        )}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(
                        house.sign_fa ||
                        house.sign ||
                        "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        house.formatted ||
                        "—"
                    )}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* ---------------------------------------------------------
   Natal aspects
--------------------------------------------------------- */

function renderNatalAspects(data) {

    const container = $("natalAspectTable");

    if (!container) return;

    const aspects = safeArray(data.aspects);

    if (!aspects.length) {

        container.innerHTML = `
            <div class="empty-state">
                جنبه‌ای پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <div class="table-wrapper">
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
    `;

    for (const item of aspects) {

        const planet1 =
            item.planet1_fa ||
            item.planet1 ||
            "—";

        const planet2 =
            item.planet2_fa ||
            item.planet2 ||
            "—";

        const aspect =
            item.aspect_fa ||
            item.aspect ||
            "—";

        html += `
            <tr>
                <td>${escapeHtml(planet1)}</td>

                <td>
                    <strong>
                        ${escapeHtml(aspect)}
                    </strong>
                </td>

                <td>${escapeHtml(planet2)}</td>

                <td>
                    ${escapeHtml(formatOrb(item.orb))}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* =========================================================
   TRANSITS
   ========================================================= */

async function loadTransits() {

    showLoading(
        "transitPositions",
        "در حال دریافت موقعیت فعلی سیارات..."
    );

    showLoading(
        "transitAspectTable",
        "در حال دریافت جنبه‌های فعلی..."
    );

    showLoading(
        "natalTransitTable",
        "در حال دریافت ترانزیت‌ها..."
    );

    try {

        const data = await fetchJson("/analysis");

        analysisData = data;

        renderTransits(data);

    } catch (error) {

        console.error("Transit error:", error);

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


/* ---------------------------------------------------------
   Find transit container
--------------------------------------------------------- */

function getTransitObject(data) {

    /*
       Current backend normally returns:

       {
           status,
           natal,
           transits: {
               current_positions,
               transit_aspects,
               natal_transits
           }
       }

       But this function also supports older structures.
    */

    if (data?.transits) {
        return safeObject(data.transits);
    }

    return data || {};
}


/* ---------------------------------------------------------
   Render all transit sections
--------------------------------------------------------- */

function renderTransits(data) {

    const transits = getTransitObject(data);

    /*
       Current positions
    */

    const positions =
        transits.current_positions ||
        transits.positions ||
        data.current_positions ||
        data.positions ||
        {};

    renderTransitPositions(positions);


    /*
       Transit-to-transit aspects
    */

    const transitAspects =
        transits.transit_aspects ||
        transits.aspects ||
        data.transit_aspects ||
        [];

    renderTransitAspects(transitAspects);


    /*
       Transit-to-natal aspects
    */

    const natalTransits =
        transits.natal_transits ||
        data.natal_transits ||
        [];

    renderNatalTransitTable(natalTransits);
}


/* ---------------------------------------------------------
   Current transit positions
--------------------------------------------------------- */

function renderTransitPositions(positions) {

    const container = $("transitPositions");

    if (!container) return;

    let entries = [];

    if (Array.isArray(positions)) {

        entries = positions.map((item, index) => [
            item.planet ||
            item.name ||
            item.name_fa ||
            String(index),

            item
        ]);

    } else {

        entries = Object.entries(
            safeObject(positions)
        );
    }

    if (!entries.length) {

        container.innerHTML = `
            <div class="empty-state">
                اطلاعات آسمان امروز دریافت نشد.
            </div>
        `;

        return;
    }

    let html = `
        <div class="table-wrapper">
        <table class="astro-table">
            <thead>
                <tr>
                    <th>جرم</th>
                    <th>موقعیت فعلی</th>
                    <th>وضعیت</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [key, itemRaw] of entries) {

        const item = safeObject(itemRaw);

        const name =
            item.name_fa ||
            item.planet_fa ||
            item.planet_name_fa ||
            key;

        const position =
            item.formatted ||
            buildPosition(item) ||
            "—";

        const retrograde =
            item.retrograde
                ? "رجعتی"
                : "مستقیم";

        html += `
            <tr>
                <td>
                    <strong>
                        ${escapeHtml(item.symbol || "")}
                        ${escapeHtml(name)}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(position)}
                </td>

                <td>
                    ${escapeHtml(retrograde)}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* ---------------------------------------------------------
   Build position if formatted is unavailable
--------------------------------------------------------- */

function buildPosition(item) {

    if (
        item.degree === undefined &&
        item.degree_in_sign === undefined
    ) {
        return "";
    }

    const degree =
        item.degree ??
        Math.floor(Number(item.degree_in_sign));

    const minute =
        item.minute ??
        Math.floor(
            (
                Number(item.degree_in_sign) -
                Number(degree)
            ) * 60
        );

    const second =
        item.second ?? 0;

    const sign =
        item.sign_fa ||
        item.sign ||
        "";

    return `${degree}° ${String(minute).padStart(2, "0")}′ ${Number(second).toFixed(1).padStart(4, "0")}″ ${sign}`;
}


/* ---------------------------------------------------------
   Transit-to-transit aspects
--------------------------------------------------------- */

function renderTransitAspects(aspects) {

    const container = $("transitAspectTable");

    if (!container) return;

    aspects = safeArray(aspects);

    if (!aspects.length) {

        container.innerHTML = `
            <div class="empty-state">
                در حال حاضر جنبه قابل توجهی بین سیارات پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <div class="table-wrapper">
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
    `;

    for (const item of aspects) {

        const p1 =
            item.planet1_fa ||
            item.planet1_name_fa ||
            item.planet1 ||
            "—";

        const p2 =
            item.planet2_fa ||
            item.planet2_name_fa ||
            item.planet2 ||
            "—";

        const aspect =
            item.aspect_fa ||
            item.aspect ||
            "—";

        html += `
            <tr>
                <td>${escapeHtml(p1)}</td>

                <td>
                    <strong>
                        ${escapeHtml(aspect)}
                    </strong>
                </td>

                <td>${escapeHtml(p2)}</td>

                <td>
                    ${escapeHtml(formatOrb(item.orb))}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* ---------------------------------------------------------
   Transit -> natal
--------------------------------------------------------- */

function renderNatalTransitTable(items) {

    const container = $("natalTransitTable");

    if (!container) return;

    items = safeArray(items);

    if (!items.length) {

        container.innerHTML = `
            <div class="empty-state">
                ترانزیت مهمی نسبت به چارت تولد پیدا نشد.
            </div>
        `;

        return;
    }

    /*
       Sort by importance first,
       then smallest orb.
    */

    const sorted = [...items].sort((a, b) => {

        const importanceA =
            Number(a.importance ?? 0);

        const importanceB =
            Number(b.importance ?? 0);

        if (importanceA !== importanceB) {
            return importanceB - importanceA;
        }

        return (
            Number(a.orb ?? 999) -
            Number(b.orb ?? 999)
        );
    });

    let html = `
        <div class="table-wrapper">
        <table class="astro-table">
            <thead>
                <tr>
                    <th>ترانزیت</th>
                    <th>جنبه</th>
                    <th>جرم تولدی</th>
                    <th>خانه</th>
                    <th>Orb</th>
                    <th>قدرت</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const item of sorted) {

        const transit =
            item.transit_planet_fa ||
            item.transit_name_fa ||
            item.planet1_fa ||
            item.transit_planet ||
            item.planet1 ||
            "—";

        const natal =
            item.natal_planet_fa ||
            item.natal_name_fa ||
            item.planet2_fa ||
            item.natal_planet ||
            item.planet2 ||
            "—";

        const aspect =
            item.aspect_fa ||
            item.aspect ||
            "—";

        const house =
            item.natal_house_name_fa ||
            item.house_name_fa ||
            (
                item.natal_house
                    ? `خانه ${item.natal_house}`
                    : ""
            ) ||
            "—";

        const orb =
            formatOrb(item.orb);

        const importance =
            item.importance !== undefined
                ? item.importance
                : "—";

        html += `
            <tr>
                <td>
                    <strong>
                        ${escapeHtml(transit)}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(aspect)}
                </td>

                <td>
                    ${escapeHtml(natal)}
                </td>

                <td>
                    ${escapeHtml(house)}
                </td>

                <td>
                    ${escapeHtml(orb)}
                </td>

                <td>
                    ${escapeHtml(importance)}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
        </div>
    `;

    container.innerHTML = html;
}


/* =========================================================
   LOAD EVERYTHING
   ========================================================= */

async function loadAll() {

    /*
       Run independently so one failure
       doesn't stop the other sections.
    */

    await Promise.allSettled([
        loadNatal(),
        loadTransits()
    ]);
}


/* =========================================================
   ADVISOR
   ========================================================= */

async function askAdvisor() {

    const input = $("questionInput");
    const box = $("advisorBox");

    if (!input || !box) return;

    const question = input.value.trim();

    if (!question) {

        box.innerHTML += `
            <div class="advisor-message advisor-error">
                لطفاً سؤال خود را وارد کنید.
            </div>
        `;

        return;
    }

    /*
       User message
    */

    box.innerHTML += `
        <div class="advisor-message user-message">
            ${escapeHtml(question)}
        </div>
    `;

    input.value = "";

    /*
       Temporary loading
    */

    const loadingId =
        "advisor-loading-" +
        Date.now();

    box.innerHTML += `
        <div
            class="advisor-message assistant-message"
            id="${loadingId}"
        >
            در حال تحلیل چارت و آسمان فعلی...
        </div>
    `;

    box.scrollTop = box.scrollHeight;

    try {

        const result = await fetchJson("/advisor", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question,
                history: advisorHistory.slice(-12)
            }),

            timeout: 45000
        });

        /*
           Save conversation
        */

        advisorHistory.push({
            role: "user",
            content: question
        });

        if (result.answer) {

            advisorHistory.push({
                role: "assistant",
                content: result.answer
            });
        }

        /*
           Replace loading
        */

        const loadingEl = $(loadingId);

        if (loadingEl) {

            loadingEl.outerHTML = `
                <div class="advisor-message assistant-message">
                    ${formatAdvisorText(
                        result.answer ||
                        result.message ||
                        "پاسخی دریافت نشد."
                    )}
                </div>
            `;

        }

    } catch (error) {

        console.error("Advisor error:", error);

        const loadingEl = $(loadingId);

        if (loadingEl) {

            loadingEl.outerHTML = `
                <div class="advisor-message advisor-error">
                    خطا در ارتباط با مشاور:
                    ${escapeHtml(error.message)}
                </div>
            `;
        }
    }

    box.scrollTop = box.scrollHeight;
}


/* ---------------------------------------------------------
   Advisor text formatter
--------------------------------------------------------- */

function formatAdvisorText(text) {

    if (!text) return "";

    /*
       Escape first.
    */

    let output = escapeHtml(text);

    /*
       Preserve simple line breaks.
    */

    output = output.replace(/\n/g, "<br>");

    /*
       Basic bold support
    */

    output = output.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    return output;
}


/* ---------------------------------------------------------
   Enter key support
--------------------------------------------------------- */

document.addEventListener("DOMContentLoaded", () => {

    const input = $("questionInput");

    if (input) {

        input.addEventListener("keydown", (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {
                event.preventDefault();
                askAdvisor();
            }
        });
    }

    /*
       Do not automatically call loadAll here
       if the existing page already calls it.
    */
});


/* =========================================================
   Debug helper
   ========================================================= */

window.AstroApp = {
    getNatalData: () => natalData,
    getAnalysisData: () => analysisData,
    getAdvisorHistory: () => advisorHistory
};


/* =========================================================
   Global exports
   ========================================================= */

window.loadAll = loadAll;
window.loadNatal = loadNatal;
window.loadTransits = loadTransits;
window.askAdvisor = askAdvisor;
