document.addEventListener("DOMContentLoaded", () => {

    let advisorHistory = [];

    const questionInput =
        document.getElementById(
            "questionInput"
        );

    const advisorBox =
        document.getElementById(
            "advisorBox"
        );


    // =====================================================
    // Helpers
    // =====================================================

    function escapeHtml(value) {

        return String(
            value ?? ""
        )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
    }


    // =====================================================
    // Advisor UI
    // =====================================================

    function setupAdvisorChat() {

        if (!questionInput) {
            return;
        }

        if (!advisorBox) {
            return;
        }


        const textarea =
            questionInput;

        textarea.placeholder =
            "سؤال خود را برای مشاور بنویسید...";


        textarea.style.minHeight =
            "80px";


        textarea.style.marginBottom =
            "8px";


        const sendButton =
            document.querySelector(
                '[onclick*="advisor"]'
            );


        if (sendButton) {

            sendButton.removeAttribute(
                "onclick"
            );

            sendButton.addEventListener(
                "click",
                sendAdvisorMessage
            );
        }


        advisorBox.classList.add(
            "advisor-chat"
        );


        advisorBox.innerHTML = `
            <div class="advisor-welcome">
                🔮 <strong>مشاور نجومی شخصی</strong>
                <div>
                    سؤال خودت را بپرس.
                    اگر برای تحلیل دقیق‌تر اطلاعاتی لازم باشد،
                    مشاور ابتدا از خودت سؤال می‌پرسد.
                </div>
            </div>
        `;
    }


    // =====================================================
    // Render message
    // =====================================================

    function addMessage(
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


    // =====================================================
    // Format response
    // =====================================================

    function formatAdvisorText(
        text
    ) {

        let html =
            escapeHtml(text);


        html = html.replace(
            /^### (.+)$/gm,
            "<div class=\"advisor-heading\">$1</div>"
        );


        html = html.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


        html = html.replace(
            /\n/g,
            "<br>"
        );


        return html;
    }


    // =====================================================
    // Loading
    // =====================================================

    function addLoading() {

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
                در حال بررسی چارت تولد و آسمان فعلی...
            </div>
        `;


        advisorBox.appendChild(
            loading
        );


        advisorBox.scrollTop =
            advisorBox.scrollHeight;
    }


    function removeLoading() {

        const loading =
            document.getElementById(
                "advisorLoading"
            );


        if (loading) {
            loading.remove();
        }
    }


    // =====================================================
    // Send message
    // =====================================================

    async function sendAdvisorMessage() {

        if (!questionInput) {
            return;
        }


        const question =
            questionInput.value.trim();


        if (!question) {
            return;
        }


        addMessage(
            "user",
            question
        );


        questionInput.value =
            "";


        addLoading();


        try {

            const response =
                await fetch(
                    "/advisor",
                    {
                        method:
                            "POST",

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
                    }
                );


            const data =
                await response.json();


            removeLoading();


            if (
                !response.ok
                ||
                data.status === "error"
            ) {

                addMessage(
                    "assistant",
                    data.message
                    ||
                    "مشاور نتوانست پاسخ دهد."
                );

                return;
            }


            // ذخیره تاریخچه
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
                    data.message
                    ||
                    ""
            });


            // محدود کردن تاریخچه
            if (
                advisorHistory.length
                > 12
            ) {

                advisorHistory =
                    advisorHistory.slice(
                        -12
                    );
            }


            addMessage(
                "assistant",
                data.message
                ||
                "پاسخی دریافت نشد."
            );


        } catch (error) {

            removeLoading();


            console.error(
                "Advisor error:",
                error
            );


            addMessage(
                "assistant",
                "ارتباط با مشاور برقرار نشد. لطفاً دوباره تلاش کن."
            );
        }
    }


    // =====================================================
    // Enter to send
    // =====================================================

    if (questionInput) {

        questionInput.addEventListener(
            "keydown",
            (event) => {

                if (
                    event.key === "Enter"
                    &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendAdvisorMessage();
                }
            }
        );
    }


    // =====================================================
    // Initialize
    // =====================================================

    setupAdvisorChat();

});
