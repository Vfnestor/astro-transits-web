"use strict";


const $ = (id) =>
    document.getElementById(id);


// =========================================================
// API // Deploy sync 2026-09-02
// =========================================================

async function api(
    url,
    options = {}
) {

    const response = await fetch(
        url,
        options
    );

    const data =
        await response.json();

    if (!response.ok) {

        throw new Error(
            data.error ||
            "خطا در دریافت اطلاعات"
        );

    }

    if (data.status === "error") {

        throw new Error(
            data.error ||
            "خطای سرور"
        );

    }

    return data;
}


// =========================================================
// Position
// =========================================================

function positionText(
    position
) {

    if (!position) {
        return "—";
    }

    return (
        `${position.degree}° ` +
        `${String(position.minute).padStart(2, "0")}′ ` +
        `${position.sign_fa}`
    );
}


// =========================================================
// Error
// =========================================================

function showError(
    element,
    error
) {

    element.innerHTML =
        `<div class="error">
            خطا: ${escapeHtml(error.message || error)}
        </div>`;
}


// =========================================================
// Escape
// =========================================================

function escapeHtml(
    value
) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =========================================================
// Natal
// =========================================================

async function loadNatal() {

    try {

        const data =
            await api("/natal");

        const planets =
            data.planets;

        $("sunPosition").textContent =
            positionText(
                planets.Sun
            );

        $("moonPosition").textContent =
            positionText(
                planets.Moon
            );

        $("ascPosition").textContent =
            positionText(
                data.angles.ascendant
            );

        $("mcPosition").textContent =
            positionText(
                data.angles.mc
            );


        renderPlanets(
            data
        );

        renderHouses(
            data.houses
        );

        renderNatalAspects(
            data.aspects
        );

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

function renderPlanets(
    data
) {

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


    const bodies = {
        ...data.planets,
        ...data.nodes
    };


    for (
        const [name, body]
        of Object.entries(bodies)
    ) {

        const retro =
            body.retrograde
                ? `<span class="retrograde">℞ برگشتی</span>`
                : "مستقیم";


        html += `
            <tr>

                <td>
                    ${body.symbol || ""}
                    ${escapeHtml(body.name_fa || name)}
                </td>

                <td>
                    ${positionText(body)}
                </td>

                <td>
                    ${body.house || "—"}
                    ${escapeHtml(
                        body.house_name_fa || ""
                    )}
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


    $("planetTable").innerHTML =
        html;
}


// =========================================================
// Houses
// =========================================================

function renderHouses(
    houses
) {

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


    for (
        const [number, house]
        of Object.entries(houses)
    ) {

        html += `
            <tr>

                <td>
                    ${escapeHtml(
                        house.name_fa
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


    $("houseTable").innerHTML =
        html;
}


// =========================================================
// Natal aspects
// =========================================================

function renderNatalAspects(
    aspects
) {

    if (!aspects.length) {

        $("natalAspectTable").innerHTML =
            `<div class="loading">
                جنبه قابل توجهی پیدا نشد.
            </div>`;

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


    aspects.forEach(
        (aspect) => {

            html += `
                <tr>

                    <td>
                        ${escapeHtml(
                            aspect.planet1_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            aspect.aspect_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            aspect.planet2_fa
                        )}
                    </td>

                    <td>
                        ${aspect.orb.toFixed(2)}°
                    </td>

                </tr>
            `;
        }
    );


    html += `
            </tbody>
        </table>
    `;


    $("natalAspectTable").innerHTML =
        html;
}


// =========================================================
// Transits
// =========================================================

async function loadTransits() {

    try {

        const data =
            await api("/analysis");


        renderTransitPositions(
            data.current_positions
        );


        renderTransitAspects(
            data.transit_aspects
        );


        renderNatalTransits(
            data.natal_transits
        );

    } catch (error) {

        showError(
            $("transitPositions"),
            error
        );
    }
}


// =========================================================
// Transit positions
// =========================================================

function renderTransitPositions(
    positions
) {

    let html = "";


    for (
        const [name, body]
        of Object.entries(positions)
    ) {

        html += `
            <div class="planet-card">

                <div class="planet-symbol">
                    ${body.symbol}
                </div>

                <div class="planet-name">
                    ${escapeHtml(
                        body.name_fa
                    )}
                </div>

                <div class="planet-position">
                    ${positionText(body)}
                </div>

                ${
                    body.retrograde
                    ? `<div class="retrograde">
                        ℞ برگشتی
                       </div>`
                    : ""
                }

            </div>
        `;
    }


    $("transitPositions").innerHTML =
        html;
}


// =========================================================
// Transit aspects
// =========================================================

function renderTransitAspects(
    aspects
) {

    if (!aspects.length) {

        $("transitAspectTable").innerHTML =
            `<div class="loading">
                در حال حاضر جنبه قابل توجهی
                بین سیارات پیدا نشد.
            </div>`;

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


    aspects.forEach(
        (a) => {

            html += `
                <tr>

                    <td>
                        ${escapeHtml(
                            a.planet1_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            a.aspect_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            a.planet2_fa
                        )}
                    </td>

                    <td>
                        ${a.orb.toFixed(2)}°
                    </td>

                </tr>
            `;
        }
    );


    html += `
            </tbody>
        </table>
    `;


    $("transitAspectTable").innerHTML =
        html;
}


// =========================================================
// Natal transit aspects
// =========================================================

function renderNatalTransits(
    aspects
) {

    if (!aspects.length) {

        $("natalTransitTable").innerHTML =
            `<div class="loading">
                ترانزیت مهمی نسبت به چارت تولد
                در محدوده فعلی پیدا نشد.
            </div>`;

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


    aspects.forEach(
        (a) => {

            html += `
                <tr>

                    <td>
                        ${escapeHtml(
                            a.transit_planet_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            a.aspect_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            a.natal_planet_fa
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            a.natal_house_name_fa || "—"
                        )}
                    </td>

                    <td>
                        ${a.orb.toFixed(2)}°
                    </td>

                </tr>
            `;
        }
    );


    html += `
            </tbody>
        </table>
    `;


    $("natalTransitTable").innerHTML =
        html;
}


// =========================================================
// Advisor
// =========================================================

async function askAdvisor() {

    const input =
        $("questionInput");

    const box =
        $("advisorBox");

    const question =
        input.value.trim();


    if (!question) {

        box.textContent =
            "لطفاً ابتدا سؤال خودت را بنویس.";

        return;
    }


    box.textContent =
        "در حال بررسی چارت تولد و ترانزیت‌ها...";


    try {

        const data =
            await api(
                "/advisor",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        question
                    }),
                }
            );


        box.textContent =
            data.advice;

    } catch (error) {

        box.textContent =
            "خطا: " +
            error.message;
    }
}


// =========================================================
// Dashboard
// =========================================================

async function loadAll() {

    await Promise.all([
        loadNatal(),
        loadTransits(),
    ]);
}


// =========================================================
// Initial load
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAll();

    }
);
