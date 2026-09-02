"use strict";

// =========================================================
// Helpers
// =========================================================

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function positionText(position) {
    if (!position || typeof position !== "object") {
        return "—";
    }

    const degree = position.degree ?? "—";
    const minute = String(position.minute ?? 0).padStart(2, "0");
    const sign = position.sign_fa ?? "";

    return `${degree}° ${minute}′ ${sign}`;
}

function safeArray(value) {
    return Array.isArray(value) ? value : [];
}

function safeObject(value) {
    return value &&
        typeof value === "object" &&
        !Array.isArray(value)
        ? value
        : {};
}

// =========================================================
// API
// =========================================================

async function api(url, options = {}) {

    const response = await fetch(url, options);

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("پاسخ نامعتبر از سرور دریافت شد.");
    }

    if (!response.ok) {
        throw new Error(
            data?.error || "خطا در دریافت اطلاعات"
        );
    }

    if (data?.status === "error") {
        throw new Error(
            data?.error || "خطای سرور"
        );
    }

    return data;
}

// =========================================================
// Error
// =========================================================

function showError(element, error) {

    if (!element) {
        return;
    }

    element.innerHTML = `
        <div class="error">
            خطا: ${escapeHtml(error?.message || error)}
        </div>
    `;
}

// =========================================================
// Natal Chart
// =========================================================

async function loadNatal() {

    try {

        const data = await api("/natal");

        const planets = safeObject(data?.planets);
        const angles = safeObject(data?.angles);

        const sun = $("sunPosition");
        const moon = $("moonPosition");
        const asc = $("ascPosition");
        const mc = $("mcPosition");

        if (sun) {
            sun.textContent = positionText(planets.Sun);
        }

        if (moon) {
            moon.textContent = positionText(planets.Moon);
        }

        if (asc) {
            asc.textContent =
                positionText(angles.ascendant);
        }

        if (mc) {
            mc.textContent =
                positionText(angles.mc);
        }

        renderPlanets(data);
        renderHouses(data?.houses);
        renderNatalAspects(data?.aspects);

    } catch (error) {

        showError(
            $("planetTable"),
            error
        );
    }
}

// =========================================================
// Planets
// =========================================================

function renderPlanets(data) {

    const planets = safeObject(data?.planets);
    const nodes = safeObject(data?.nodes);

    const bodies = {
        ...planets,
        ...nodes
    };

    const container = $("planetTable");

    if (!container) {
        return;
    }

    if (!Object.keys(bodies).length) {

        container.innerHTML = `
            <div class="loading">
                اطلاعات سیارات تولد دریافت نشد.
            </div>
        `;

        return;
    }

    let html = `
        <table>
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

    for (const [name, body] of Object.entries(bodies)) {

        const retro = body?.retrograde
            ? `<span class="retrograde">℞ برگشتی</span>`
            : "مستقیم";

        html += `
            <tr>
                <td>
                    ${escapeHtml(body?.symbol || "")}
                    ${escapeHtml(body?.name_fa || name)}
                </td>

                <td>
                    ${positionText(body)}
                </td>

                <td>
                    ${escapeHtml(body?.house ?? "—")}
                    ${escapeHtml(body?.house_name_fa || "")}
                </td>

                <td>
                    ${retro}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// =========================================================
// Houses
// =========================================================

function renderHouses(houses) {

    const container = $("houseTable");

    if (!container) {
        return;
    }

    houses = safeObject(houses);

    if (!Object.keys(houses).length) {

        container.innerHTML = `
            <div class="loading">
                اطلاعات خانه‌ها دریافت نشد.
            </div>
        `;

        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>خانه</th>
                    <th>آغاز خانه</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [number, house] of Object.entries(houses)) {

        html += `
            <tr>
                <td>
                    ${escapeHtml(
                        house?.name_fa || `خانه ${number}`
                    )}
                </td>

                <td>
                    ${positionText(house)}
                </td>
            </tr>
        `;
    }

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// =========================================================
// Natal Aspects
// =========================================================

function renderNatalAspects(aspects) {

    const container = $("natalAspectTable");

    if (!container) {
        return;
    }

    aspects = safeArray(aspects);

    if (!aspects.length) {

        container.innerHTML = `
            <div class="loading">
                جنبه قابل توجهی پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <table>
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

    aspects.forEach((aspect) => {

        const orb = Number(aspect?.orb);

        html += `
            <tr>
                <td>
                    ${escapeHtml(
                        aspect?.planet1_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        aspect?.aspect_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        aspect?.planet2_fa || "—"
                    )}
                </td>

                <td>
                    ${
                        Number.isFinite(orb)
                            ? orb.toFixed(2) + "°"
                            : "—"
                    }
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// =========================================================
// Transits
// =========================================================

async function loadTransits() {

    try {

        const data = await api("/analysis");

        /*
         * ساختار API:
         *
         * data
         * ├── natal
         * └── transits
         *     ├── current_positions
         *     ├── transit_aspects
         *     └── natal_transits
         */

        const transits = safeObject(data?.transits);

        renderTransitPositions(
            transits.current_positions
        );

        renderTransitAspects(
            transits.transit_aspects
        );

        renderNatalTransits(
            transits.natal_transits
        );

    } catch (error) {

        showError(
            $("transitPositions"),
            error
        );
    }
}

// =========================================================
// Current Sky
// =========================================================

function renderTransitPositions(positions) {

    const container = $("transitPositions");

    if (!container) {
        return;
    }

    positions = safeObject(positions);

    if (!Object.keys(positions).length) {

        container.innerHTML = `
            <div class="loading">
                اطلاعات آسمان امروز دریافت نشد.
            </div>
        `;

        return;
    }

    let html = "";

    for (const [name, body] of Object.entries(positions)) {

        html += `
            <div class="planet-card">

                <div class="planet-symbol">
                    ${escapeHtml(body?.symbol || "")}
                </div>

                <div class="planet-name">
                    ${escapeHtml(
                        body?.name_fa || name
                    )}
                </div>

                <div class="planet-position">
                    ${positionText(body)}
                </div>

                ${
                    body?.retrograde
                        ? `
                            <div class="retrograde">
                                ℞ برگشتی
                            </div>
                        `
                        : ""
                }

            </div>
        `;
    }

    container.innerHTML = html;
}

// =========================================================
// Transit Aspects
// =========================================================

function renderTransitAspects(aspects) {

    const container = $("transitAspectTable");

    if (!container) {
        return;
    }

    aspects = safeArray(aspects);

    if (!aspects.length) {

        container.innerHTML = `
            <div class="loading">
                در حال حاضر جنبه قابل توجهی
                بین سیارات پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>سیاره</th>
                    <th>جنبه</th>
                    <th>سیاره</th>
                    <th>Orb</th>
                </tr>
            </thead>
            <tbody>
    `;

    aspects.forEach((a) => {

        const orb = Number(a?.orb);

        html += `
            <tr>

                <td>
                    ${escapeHtml(
                        a?.planet1_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        a?.aspect_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        a?.planet2_fa || "—"
                    )}
                </td>

                <td>
                    ${
                        Number.isFinite(orb)
                            ? orb.toFixed(2) + "°"
                            : "—"
                    }
                </td>

            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// =========================================================
// Natal Transit Aspects
// =========================================================

function renderNatalTransits(aspects) {

    const container = $("natalTransitTable");

    if (!container) {
        return;
    }

    aspects = safeArray(aspects);

    if (!aspects.length) {

        container.innerHTML = `
            <div class="loading">
                ترانزیت مهمی نسبت به چارت تولد
                در محدوده فعلی پیدا نشد.
            </div>
        `;

        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ترانزیت</th>
                    <th>جنبه</th>
                    <th>جرم تولدی</th>
                    <th>خانه</th>
                    <th>Orb</th>
                </tr>
            </thead>
            <tbody>
    `;

    aspects.forEach((a) => {

        const orb = Number(a?.orb);

        html += `
            <tr>

                <td>
                    ${escapeHtml(
                        a?.transit_planet_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        a?.aspect_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        a?.natal_planet_fa || "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        a?.natal_house_name_fa || "—"
                    )}
                </td>

                <td>
                    ${
                        Number.isFinite(orb)
                            ? orb.toFixed(2) + "°"
                            : "—"
                    }
                </td>

            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// =========================================================
// Advisor
// =========================================================

async function askAdvisor() {

    const input = $("questionInput");
    const box = $("advisorBox");

    if (!input || !box) {
        return;
    }

    const question = input.value.trim();

    if (!question) {

        box.textContent =
            "لطفاً ابتدا سؤال خودت را بنویس.";

        return;
    }

    box.textContent =
        "در حال بررسی چارت تولد و ترانزیت‌ها...";

    try {

        const data = await api(
            "/advisor",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question
                })
            }
        );

        if (data?.advice) {

            box.textContent =
                data.advice;

        } else {

            box.textContent =
                "پاسخ مشاور دریافت نشد.";
        }

    } catch (error) {

        box.textContent =
            "خطا: " +
            (error?.message || error);
    }
}

// =========================================================
// Dashboard
// =========================================================

async function loadAll() {

    await Promise.all([
        loadNatal(),
        loadTransits()
    ]);
}

// =========================================================
// Initial Load
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAll();

    }
);
