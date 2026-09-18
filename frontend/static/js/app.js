window.currentConversationId = null;

const sendButton =
    document.getElementById("send-btn");

const input =
    document.getElementById("question");

// ======================================================
// Auto Resize Question Input
// ======================================================

function autoResizeInput() {

    input.style.height = "24px";


    const newHeight =
        Math.min(
            input.scrollHeight,
            150
        );


    input.style.height =
        newHeight + "px";

}

input.addEventListener(
    "input",
    autoResizeInput
);

const chatBox =
    document.getElementById("chat-box");


// ======================================================
// Initial Screen State
// ======================================================

window.setInitialState = function (isInitial) {

    const mainContent =
        document.querySelector(".main-content");

    if (!mainContent) {
        return;
    }

    if (isInitial) {

        mainContent.classList.add("initial-state");

    } else {

        mainContent.classList.remove("initial-state");

    }

};


// ======================================================
// EVENTS
// ======================================================

sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter" && !event.shiftKey) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ======================================================
// UI Message
// ======================================================

function addUserMessage(message) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "user-message";


    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble-user";

    bubble.textContent =
        message;


    // Copy button
    const copyButton =
        document.createElement("button");

    copyButton.className =
        "copy-button";

    // copyButton.textContent =
    //     "📋";

    copyButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24"
            fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
    `;

    copyButton.title =
        "Copy pertanyaan";


    copyButton.addEventListener(
        "click",
        async function () {

            try {

                await navigator.clipboard.writeText(
                    message
                );

                // copyButton.textContent =
                //     "✓ Copied";
                copyButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                `;

                setTimeout(
                    function () {

                        copyButton.innerHTML = `
                            <svg width="16" height="16" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                        `;

                    },
                    1500
                );

            }
            catch (error) {

                console.error(
                    "Copy error:",
                    error
                );

            }

        }
    );

    
    bubble.appendChild(copyButton);

    wrapper.appendChild(bubble);

    chatBox.appendChild(wrapper);


    chatBox.scrollTop =
        chatBox.scrollHeight;

}


function addAIMessage(message) {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "ai-message";


    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble-ai";

    bubble.textContent =
        message;


    // Copy button
    const copyButton =
        document.createElement("button");

    copyButton.className =
        "copy-button";

    copyButton.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24"
            fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
    `;

    copyButton.title =
        "Copy jawaban EVE";


    copyButton.addEventListener(
        "click",
        async function () {

            try {

                await navigator.clipboard.writeText(
                    message
                );

                copyButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24"
                        fill="none" stroke="currentColor"
                        stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                `;

                setTimeout(
                    function () {

                        copyButton.innerHTML = `
                            <svg width="16" height="16" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor"
                                stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round">
                                <rect x="9" y="9" width="13" height="13" rx="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                        `;

                    },
                    1500
                );

            }
            catch (error) {

                console.error(
                    "Copy error:",
                    error
                );

            }

        }
    );


    // wrapper.appendChild(bubble);

    // wrapper.appendChild(copyButton);

    // chatBox.appendChild(wrapper);


    bubble.appendChild(copyButton);


    wrapper.appendChild(bubble);


    chatBox.appendChild(wrapper);

    chatBox.scrollTop =
        chatBox.scrollHeight;

}


// ======================================================
// Send Message
// ======================================================

async function sendMessage() {

    const message =
        input.value.trim();


    if (message === "") {

        return;

    }



    // ==========================================
// Jika belum ada conversation
// ==========================================

if (
    window.currentConversationId === null ||
    window.currentConversationId === undefined ||
    window.currentConversationId === ""
) {

    const newConversationId =
        await createNewChat(false);


    if (!newConversationId) {

        console.error(
            "Conversation gagal dibuat."
        );

        return;

    }

}



    // ==========================================
    // Keluar dari Initial Screen
    // ==========================================

    window.setInitialState(false);


    // ==========================================
    // User Message
    // ==========================================

    addUserMessage(message);


    input.value = "";

    input.style.height = "24px";


    // ==========================================
    // Loading
    // ==========================================

    const loadingId =
        "loading-" + Date.now();


    chatBox.innerHTML += `

        <div
            id="${loadingId}"
            class="ai-message">

            <div class="bubble-loading">

                ⏳ EVE sedang berpikir...

            </div>

        </div>

    `;


    chatBox.scrollTop =
        chatBox.scrollHeight;


    // ==========================================
    // Call Chat API
    // ==========================================

    try {

        const response =
            await fetch(

                `/api/chat/${window.currentConversationId}`,

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        message:
                            message

                    })

                }

            );


        if (!response.ok) {

            throw new Error(
                `Chat API error: ${response.status}`
            );

        }


        const data =
            await response.json();


        // ======================================
        // Remove Loading
        // ======================================

        document
            .getElementById(loadingId)
            ?.remove();


        // ======================================
        // AI Response
        // ======================================

        addAIMessage(
            data.answer
        );


        // ======================================
        // Update Chat History Title
        // ======================================

        if (
            data.title &&
            typeof updateConversationTitle ===
                "function"
        ) {

            updateConversationTitle(
                data.conversation_id,
                data.title
            );

        }

    }


    catch (error) {

        document
            .getElementById(loadingId)
            ?.remove();


        addAIMessage(
            "Gagal menghubungi EVE."
        );


        console.error(
            "Send message error:",
            error
        );

    }

}


// ======================================================
// Welcome Screen
// ======================================================

function hideWelcome() {

    const welcome =
        document.querySelector(
            ".welcome"
        );


    if (welcome) {

        welcome.remove();

    }

}



function formatModelName(model) {

    if (
        model ===
        "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
    ) {
        return "Qwen 2.5 3B";
    }

    if (
        model ===
        "llama-3.2-3b-instruct-q4_k_m.gguf"
    ) {
        return "Llama 3.2 3B";
    }

    if (
        model ===
        "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf"
    ) {
        return "Phi-4 Mini 3.8B";
    }

    return model
        .replace(".gguf", "")
        .replace(/[-_]/g, " ");
}


// ======================================================
// MODEL SELECTOR
// ======================================================

const modelSelect =
    document.getElementById("model-select");


// Load available models
async function loadModels() {

    try {

        const response =
            await fetch("/api/models");

        if (!response.ok) {

            throw new Error(
                `Model API error: ${response.status}`
            );

        }

        const data =
            await response.json();


        // Bersihkan dropdown
        modelSelect.innerHTML = "";

        const activeModelName =
            document.getElementById(
                "active-model-name"
            );

        if (activeModelName) {

            activeModelName.textContent =
                formatModelName(data.active_model);

        }


        // Tambahkan model
        data.models.forEach(
            function (model) {

                const option =
                    document.createElement("option");

                option.value =
                    model;

                option.textContent =
                formatModelName(model);

                if (
                    model === data.active_model
                ) {

                    option.selected = true;

                }

                modelSelect.appendChild(option);

            }
        );

    }

    catch (error) {

        console.error(
            "Load models error:",
            error
        );

        modelSelect.innerHTML =
            "<option>Model gagal dimuat</option>";

    }

}


// Change model
modelSelect.addEventListener(
    "change",
    async function () {

        const modelName =
            modelSelect.value;


        if (!modelName) {
            return;
        }


        try {

            modelSelect.disabled = true;


            const response =
                await fetch(
                    "/api/models/select",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            model_name:
                                modelName
                        })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Change model error: ${response.status}`
                );

            }


            const data =
                await response.json();


            console.log(
                "Active model:",
                data.active_model
            );

            const activeModelName =
                document.getElementById(
                    "active-model-name"
                );

            if (activeModelName) {

                activeModelName.textContent =
                    formatModelName(
                        data.active_model
                    );

            }


        }

        catch (error) {

            console.error(
                "Change model error:",
                error
            );

            alert(
                "Gagal mengganti model."
            );

            // Kembalikan pilihan sebelumnya
            loadModels();

        }

        finally {

            modelSelect.disabled = false;

        }

    }
);


// Load model saat EVE dibuka
loadModels();