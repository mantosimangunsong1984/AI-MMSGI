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


    const loadingWrapper =
    document.createElement("div");

    loadingWrapper.id =
        loadingId;

    loadingWrapper.className =
        "ai-message";


    const loadingBubble =
        document.createElement("div");

    loadingBubble.className =
        "bubble-loading";

    loadingBubble.textContent =
        "⏳ EVE sedang berpikir...";


    loadingWrapper.appendChild(
        loadingBubble
    );

    chatBox.appendChild(
        loadingWrapper
    );


    
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
        return "Phi-4 Mini Q4";
    }

    if (
        model ===
        "Qwen_Qwen3-8B-Q4_K_M.gguf"
    ) {
        return "Qwen 3 8B";
    }

    if (
        model ===
        "microsoft_Phi-4-mini-instruct-Q8_0.gguf"
    ) {
        return "Phi-4 Mini Q8";
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


// ======================================================
// LOAD AVAILABLE MODELS
// ======================================================

async function loadModels() {

    // Jika model selector tidak tersedia,
    // jangan hentikan JavaScript lainnya.
    if (!modelSelect) {
        console.warn(
            "Element #model-select tidak ditemukan."
        );
        return;
    }

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


        // ==================================================
        // UPDATE ACTIVE MODEL NAME
        // ==================================================

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


        // ==================================================
        // ADD MODELS
        // ==================================================

        data.models.forEach(
            function (model) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    model;


                option.textContent =
                    formatModelName(
                        model
                    );


                if (
                    model ===
                    data.active_model
                ) {

                    option.selected =
                        true;

                }


                modelSelect.appendChild(
                    option
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Load models error:",
            error
        );


        modelSelect.innerHTML =
            `
            <option value="">
                Model gagal dimuat
            </option>
            `;

    }

}


// ======================================================
// CHANGE MODEL
// ======================================================

if (modelSelect) {

    modelSelect.addEventListener(
        "change",
        async function () {

            const modelName =
                modelSelect.value;


            if (!modelName) {
                return;
            }


            try {

                modelSelect.disabled =
                    true;


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


                // ==================================================
                // UPDATE HEADER MODEL
                // ==================================================

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
                await loadModels();

            }

            finally {

                modelSelect.disabled =
                    false;

            }

        }
    );

}


// ======================================================
// LOAD MODEL SAAT EVE DIBUKA
// ======================================================

loadModels();




// ======================================================
// SETTINGS
// ======================================================

const settingsButton =
    document.getElementById("settings-btn");

const settingsModal =
    document.getElementById("settings-modal");

const settingsClose =
    document.getElementById("settings-close");

const settingsCloseBottom =
    document.getElementById(
        "settings-close-bottom"
    );

const settingsModelSelect =
    document.getElementById(
        "settings-model-select"
    );

const settingsDocumentList =
    document.getElementById(
        "settings-document-list"
    );


// ======================================================
// OPEN SETTINGS
// ======================================================

// ======================================================
// SETTINGS BUTTON
// ======================================================

document.addEventListener(
    "click",
    function (event) {

        const button =
            event.target.closest(
                "#settings-btn"
            );

        if (!button) {
            return;
        }

        event.preventDefault();

        openSettings();

    }
);


// ======================================================
// CLOSE SETTINGS
// ======================================================

if (settingsClose) {

    settingsClose.addEventListener(
        "click",
        closeSettings
    );

}


if (settingsCloseBottom) {

    settingsCloseBottom.addEventListener(
        "click",
        closeSettings
    );

}


// Close when clicking outside panel
if (settingsModal) {

    settingsModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                settingsModal
            ) {

                closeSettings();

            }

        }
    );

}


// Close with ESC
document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape" &&
            settingsModal &&
            !settingsModal.classList.contains("hidden")
        ) {

            closeSettings();

        }

    }
);


// ======================================================
// OPEN SETTINGS
// ======================================================


// ======================================================
// OPEN SETTINGS
// ======================================================

async function openSettings() {

    console.log(
        "Opening Settings..."
    );

    const modal =
        document.getElementById(
            "settings-modal"
        );

    if (!modal) {

        console.error(
            "ERROR: #settings-modal tidak ditemukan."
        );

        return;

    }


    modal.classList.remove(
        "hidden"
    );


    try {

        await loadSettingsModels();

        await loadDocuments();

    }

    catch (error) {

        console.error(
            "Open Settings error:",
            error
        );

    }

}


// ======================================================
// CLOSE SETTINGS
// ======================================================

function closeSettings() {

    if (!settingsModal) {
        return;
    }

    settingsModal.classList.add(
        "hidden"
    );

}


// ======================================================
// LOAD MODEL INTO SETTINGS
// ======================================================

async function loadSettingsModels() {

    if (!settingsModelSelect) {
        return;
    }

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


        settingsModelSelect.innerHTML =
            "";


        data.models.forEach(
            function (model) {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    model;

                option.textContent =
                    formatModelName(model);


                if (
                    model ===
                    data.active_model
                ) {

                    option.selected =
                        true;

                }


                settingsModelSelect.appendChild(
                    option
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Load settings models error:",
            error
        );

        settingsModelSelect.innerHTML =
            `
            <option value="">
                Model gagal dimuat
            </option>
            `;

    }

}


// ======================================================
// CHANGE MODEL FROM SETTINGS
// ======================================================

if (settingsModelSelect) {

    settingsModelSelect.addEventListener(
        "change",
        async function () {

            const modelName =
                settingsModelSelect.value;


            if (!modelName) {
                return;
            }


            try {

                settingsModelSelect.disabled =
                    true;


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


                // Update header model
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


                // Update header selector
                if (modelSelect) {

                    modelSelect.value =
                        data.active_model;

                }


                console.log(
                    "Active model:",
                    data.active_model
                );

            }

            catch (error) {

                console.error(
                    "Settings model error:",
                    error
                );

                alert(
                    "Gagal mengganti model."
                );

                await loadSettingsModels();

            }

            finally {

                settingsModelSelect.disabled =
                    false;

            }

        }
    );

}


// ======================================================
// LOAD DOCUMENTS
// ======================================================

async function loadDocuments() {

    if (!settingsDocumentList) {
        return;
    }

    settingsDocumentList.innerHTML = `
        <div class="document-loading">
            Loading documents...
        </div>
    `;

    try {

        const response = await fetch("/api/documents");

        if (!response.ok) {
            throw new Error(
                `Document API error: ${response.status}`
            );
        }

        const data = await response.json();

        const documents = data.documents || [];

        settingsDocumentList.innerHTML = "";

        if (documents.length === 0) {

            settingsDocumentList.innerHTML = `
                <div class="document-empty">
                    No documents available.
                </div>
            `;

            return;
        }

        documents.forEach(function (doc) {

            const row = document.createElement("div");

            row.className =
                "settings-document-item";


            // ==================================================
            // DOCUMENT INFO
            // ==================================================

            const info = document.createElement("div");

            info.className =
                "document-info";


            const icon = document.createElement("span");

            icon.className =
                "document-icon";

            icon.textContent =
                "📄";


            const name = document.createElement("span");

            name.className =
                "document-name";

            name.textContent =
                doc.filename;


            info.appendChild(icon);
            info.appendChild(name);


            // ==================================================
            // DOCUMENT ACTIONS
            // ==================================================

            const actions =
                document.createElement("div");

            actions.className =
                "document-actions";


            // ==================================================
            // VIEW CHUNKS BUTTON
            // ==================================================

            const chunksButton =
                document.createElement("button");

            chunksButton.type =
                "button";

            chunksButton.className =
                "document-chunks-button";

            chunksButton.textContent =
                "View Chunks";

            chunksButton.title =
                "View document chunks";


            chunksButton.addEventListener(
                "click",
                function () {

                    openChunksModal(
                        doc.filename
                    );

                }
            );


            // ==================================================
            // DELETE DOCUMENT BUTTON
            // ==================================================

            const deleteButton =
                document.createElement("button");

            deleteButton.type =
                "button";

            deleteButton.className =
                "document-delete-button";

            deleteButton.title =
                "Delete document";


            deleteButton.innerHTML = `
                <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round">

                    <polyline
                        points="3 6 5 6 21 6">
                    </polyline>

                    <path
                        d="M19 6v14a2 2 0 0 1-2 2H7
                           a2 2 0 0 1-2-2V6">
                    </path>

                    <path d="M10 11v6"></path>

                    <path d="M14 11v6"></path>

                    <path
                        d="M9 6V4
                           a2 2 0 0 1 2-2h2
                           a2 2 0 0 1 2 2v2">
                    </path>

                </svg>
            `;


            deleteButton.addEventListener(
                "click",
                function () {

                    deleteDocument(
                        doc.filename,
                        deleteButton
                    );

                }
            );


            // ==================================================
            // APPEND ACTIONS
            // ==================================================

            actions.appendChild(
                chunksButton
            );

            actions.appendChild(
                deleteButton
            );


            // ==================================================
            // APPEND ROW
            // ==================================================

            row.appendChild(info);

            row.appendChild(actions);

            settingsDocumentList.appendChild(row);

        });

    }

    catch (error) {

        console.error(
            "Load documents error:",
            error
        );

        settingsDocumentList.innerHTML = `
            <div class="document-error">
                Failed to load documents.
            </div>
        `;

    }

}


// ======================================================
// CHUNK CRUD
// ======================================================

let currentChunkFilename = null;



// ======================================================
// OPEN CHUNKS MODAL
// ======================================================

async function openChunksModal(filename) {

    currentChunkFilename = filename;

    const modal =
        createChunksModal();

    // Pastikan modal benar-benar tampil
    modal.classList.remove("hidden");

    modal.style.setProperty(
        "display",
        "flex",
        "important"
    );

    const title =
        modal.querySelector(
            ".chunks-modal-title"
        );

    if (title) {

        title.textContent =
            filename;

    }

    await loadDocumentChunks(
        filename
    );

}



// ======================================================
// CREATE CHUNKS MODAL
// ======================================================

function createChunksModal() {

    let modal =
        document.getElementById("chunks-modal");


    if (modal) {
        return modal;
    }


    modal =
        document.createElement("div");

    modal.id =
        "chunks-modal";

    modal.className =
        "chunks-modal hidden";


    modal.innerHTML = `

        <div class="chunks-panel">

            <div class="chunks-header">

                <div>

                    <h2 class="chunks-modal-title">
                        Document Chunks
                    </h2>

                    <small>
                        Knowledge Base Chunks
                    </small>

                </div>


                <button
                    type="button"
                    id="chunks-modal-close"
                    class="chunks-close"
                >
                    ×
                </button>

            </div>


            <div
                id="chunks-content"
                class="chunks-content"
            >

                <div class="document-loading">
                    Loading chunks...
                </div>

            </div>


            <div class="chunks-footer">

                <button
                    type="button"
                    id="chunks-modal-close-bottom"
                    class="settings-button"
                >
                    Close
                </button>

            </div>

        </div>

    `;


    document.body.appendChild(modal);


    // ==================================================
    // CLOSE X
    // ==================================================

    const closeButton =
        modal.querySelector(
            "#chunks-modal-close"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                closeChunksModal();

            }
        );

    }


    // ==================================================
    // CLOSE BOTTOM
    // ==================================================

    const closeBottomButton =
        modal.querySelector(
            "#chunks-modal-close-bottom"
        );


    if (closeBottomButton) {

        closeBottomButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                closeChunksModal();

            }
        );

    }


    // ==================================================
    // CLICK OUTSIDE
    // ==================================================

    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                closeChunksModal();

            }

        }
    );


    return modal;

}



// ======================================================
// CLOSE CHUNKS MODAL
// ======================================================

function closeChunksModal() {

    console.log(
        "Closing Chunks Modal..."
    );

    const modal =
        document.getElementById(
            "chunks-modal"
        );

    if (!modal) {

        console.warn(
            "#chunks-modal tidak ditemukan."
        );

        return;
    }


    // ==============================================
    // Tambahkan hidden
    // ==============================================

    modal.classList.add(
        "hidden"
    );


    // ==============================================
    // Paksa display:none
    // untuk mengatasi CSS !important
    // ==============================================

    modal.style.setProperty(
        "display",
        "none",
        "important"
    );


    console.log(
        "Chunks Modal berhasil ditutup."
    );

}







// ======================================================
// LOAD DOCUMENT CHUNKS
// ======================================================

async function loadDocumentChunks(
    filename
) {

    const content =
        document.getElementById(
            "chunks-content"
        );

    if (!content) {
        return;
    }


    content.innerHTML = `
        <div class="document-loading">
            Loading chunks...
        </div>
    `;


    try {

        const response =
            await fetch(
                `/api/documents/chunks?filename=${encodeURIComponent(filename)}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Chunk API error: ${response.status}`
            );

        }


        const chunks =
            data.chunks || [];


        // ==========================================
        // HEADER
        // ==========================================

        content.innerHTML = `

            <div class="chunks-summary">

                <span>
                    Total Chunks:
                    <strong>
                        ${data.total_chunks}
                    </strong>
                </span>

            </div>

            <div
                id="chunks-list"
                class="chunks-list">
            </div>

        `;


        const chunksList =
            document.getElementById(
                "chunks-list"
            );


        // ==========================================
        // NO CHUNKS
        // ==========================================

        if (chunks.length === 0) {

            chunksList.innerHTML = `
                <div class="document-empty">
                    No chunks available.
                </div>
            `;

            return;

        }


        // ==========================================
        // CHUNK ITEMS
        // ==========================================

        chunks.forEach(
            function (chunk) {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "chunk-item";


                // ==================================
                // CHUNK HEADER
                // ==================================

                const header =
                    document.createElement(
                        "div"
                    );

                header.className =
                    "chunk-item-header";


                const chunkNumber =
                    document.createElement(
                        "strong"
                    );

                chunkNumber.textContent =
                    `Chunk #${chunk.chunk_id}`;


                const actions =
                    document.createElement(
                        "div"
                    );

                actions.className =
                    "chunk-actions";


                // ==================================
                // VIEW BUTTON
                // ==================================

                const viewButton =
                    document.createElement(
                        "button"
                    );

                viewButton.className =
                    "chunk-view-button";

                viewButton.textContent =
                    "View";

                viewButton.addEventListener(
                    "click",
                    function () {

                        viewChunk(
                            filename,
                            chunk.chunk_id
                        );

                    }
                );


                // ==================================
                // EDIT BUTTON
                // ==================================

                const editButton =
                    document.createElement(
                        "button"
                    );

                editButton.className =
                    "chunk-edit-button";

                editButton.textContent =
                    "Edit";

                editButton.addEventListener(
                    "click",
                    function () {

                        editChunk(
                            filename,
                            chunk.chunk_id,
                            chunk.text
                        );

                    }
                );


                // ==================================
                // DELETE BUTTON
                // ==================================

                const deleteButton =
                    document.createElement(
                        "button"
                    );

                deleteButton.className =
                    "chunk-delete-button";

                deleteButton.textContent =
                    "Delete";

                deleteButton.addEventListener(
                    "click",
                    function () {

                        deleteChunk(
                            filename,
                            chunk.chunk_id
                        );

                    }
                );


                actions.appendChild(
                    viewButton
                );

                actions.appendChild(
                    editButton
                );

                actions.appendChild(
                    deleteButton
                );


                header.appendChild(
                    chunkNumber
                );

                header.appendChild(
                    actions
                );


                // ==================================
                // TEXT PREVIEW
                // ==================================

                const text =
                    document.createElement(
                        "div"
                    );

                text.className =
                    "chunk-text-preview";

                text.textContent =
                    chunk.text;


                item.appendChild(
                    header
                );

                item.appendChild(
                    text
                );


                chunksList.appendChild(
                    item
                );

            }
        );

    }

    catch (error) {

        console.error(
            "Load chunks error:",
            error
        );


        content.innerHTML = `
            <div class="document-error">
                Failed to load chunks:
                ${escapeHtml(error.message)}
            </div>
        `;

    }

}



// ======================================================
// VIEW SINGLE CHUNK
// ======================================================

async function viewChunk(
    filename,
    chunkId
) {

    try {

        const response =
            await fetch(
                `/api/documents/chunk?filename=${encodeURIComponent(filename)}&chunk_id=${chunkId}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `View chunk error: ${response.status}`
            );

        }


        // ==================================================
        // GET EXISTING MODALS
        // ==================================================

        const settingsModal =
            document.getElementById(
                "settings-modal"
            );

        const chunksModal =
            document.getElementById(
                "chunks-modal"
            );


        const settingsWasVisible =
            settingsModal &&
            !settingsModal.classList.contains(
                "hidden"
            );

        const chunksWasVisible =
            chunksModal &&
            !chunksModal.classList.contains(
                "hidden"
            );


        // ==================================================
        // HIDE PARENT MODALS
        // ==================================================

        if (settingsWasVisible) {

            settingsModal.classList.add(
                "hidden"
            );

        }


        if (chunksWasVisible) {

            chunksModal.classList.add(
                "hidden"
            );

        }


        // ==================================================
        // CREATE VIEW MODAL
        // ==================================================

        const overlay =
            document.createElement(
                "div"
            );

        overlay.className =
            "chunk-view-overlay";


        overlay.innerHTML = `

            <div class="chunk-view-modal">

                <div class="chunk-view-header">

                    <div>

                        <h3>
                            View Chunk #${data.chunk_id}
                        </h3>

                        <small>
                            ${filename}
                        </small>

                    </div>


                    <button
                        type="button"
                        class="chunk-view-close"
                    >
                        ×
                    </button>

                </div>


                <div class="chunk-view-body">

                    <label>
                        Chunk Content
                    </label>

                    <div
                        class="chunk-view-text"
                    ></div>

                </div>


                <div class="chunk-view-footer">

                    <button
                        type="button"
                        class="chunk-view-close-button"
                    >
                        Close
                    </button>

                </div>

            </div>

        `;


        document.body.appendChild(
            overlay
        );


        // ==================================================
        // TEXT
        // ==================================================

        const textContainer =
            overlay.querySelector(
                ".chunk-view-text"
            );


        textContainer.textContent =
            data.text || "";


        // ==================================================
        // CLOSE MODAL
        // ==================================================

        function closeModal() {

            overlay.remove();


            // Restore chunks modal
            if (
                chunksWasVisible &&
                chunksModal
            ) {

                chunksModal.classList.remove(
                    "hidden"
                );

            }


            // Restore settings modal
            if (
                settingsWasVisible &&
                settingsModal
            ) {

                settingsModal.classList.remove(
                    "hidden"
                );

            }


            document.removeEventListener(
                "keydown",
                escHandler
            );

        }


        // ==================================================
        // CLOSE BUTTON
        // ==================================================

        const closeButton =
            overlay.querySelector(
                ".chunk-view-close"
            );

        const closeBottomButton =
            overlay.querySelector(
                ".chunk-view-close-button"
            );


        if (closeButton) {

            closeButton.addEventListener(
                "click",
                closeModal
            );

        }


        if (closeBottomButton) {

            closeBottomButton.addEventListener(
                "click",
                closeModal
            );

        }


        // ==================================================
        // CLICK OUTSIDE
        // ==================================================

        overlay.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === overlay
                ) {

                    closeModal();

                }

            }
        );


        // ==================================================
        // ESC
        // ==================================================

        function escHandler(event) {

            if (
                event.key === "Escape"
            ) {

                closeModal();

            }

        }


        document.addEventListener(
            "keydown",
            escHandler
        );

    }

    catch (error) {

        console.error(
            "View chunk error:",
            error
        );


        alert(
            `Gagal membuka chunk:\n\n${error.message}`
        );

    }

}


// ======================================================
// EDIT CHUNK
// ======================================================

async function editChunk(
    filename,
    chunkId,
    currentText
) {

    // ==================================================
    // GET EXISTING MODALS
    // ==================================================

    const settingsModal =
        document.getElementById(
            "settings-modal"
        );

    const chunksModal =
        document.getElementById(
            "chunks-modal"
        );


    const settingsWasVisible =
        settingsModal &&
        !settingsModal.classList.contains(
            "hidden"
        );

    const chunksWasVisible =
        chunksModal &&
        !chunksModal.classList.contains(
            "hidden"
        );


    // ==================================================
    // HIDE PARENT MODALS
    // ==================================================

    if (settingsWasVisible) {

        settingsModal.classList.add(
            "hidden"
        );

    }


    if (chunksWasVisible) {

        chunksModal.classList.add(
            "hidden"
        );

    }


    // ==================================================
    // CREATE EDIT MODAL
    // ==================================================

    const overlay =
        document.createElement(
            "div"
        );

    overlay.className =
        "chunk-edit-overlay";


    overlay.innerHTML = `

        <div class="chunk-edit-modal">

            <div class="chunk-edit-header">

                <div>

                    <h3>
                        Edit Chunk #${chunkId}
                    </h3>

                    <small>
                        ${filename}
                    </small>

                </div>


                <button
                    type="button"
                    class="chunk-edit-close"
                >
                    ×
                </button>

            </div>


            <div class="chunk-edit-body">

                <label>
                    Chunk Content
                </label>


                <textarea
                    class="chunk-edit-textarea"
                ></textarea>

            </div>


            <div class="chunk-edit-footer">

                <button
                    type="button"
                    class="chunk-edit-cancel"
                >
                    Cancel
                </button>


                <button
                    type="button"
                    class="chunk-edit-save"
                >
                    Save Changes
                </button>

            </div>

        </div>

    `;


    // ==================================================
    // APPEND TO BODY
    // ==================================================

    document.body.appendChild(
        overlay
    );


    // ==================================================
    // ELEMENTS
    // ==================================================

    const textarea =
        overlay.querySelector(
            ".chunk-edit-textarea"
        );

    const closeButton =
        overlay.querySelector(
            ".chunk-edit-close"
        );

    const cancelButton =
        overlay.querySelector(
            ".chunk-edit-cancel"
        );

    const saveButton =
        overlay.querySelector(
            ".chunk-edit-save"
        );


    // ==================================================
    // SET TEXT
    // ==================================================

    textarea.value =
        currentText || "";

    textarea.focus();

    textarea.setSelectionRange(
        0,
        0
    );


    // ==================================================
    // CLOSE
    // ==================================================

    function closeModal() {

        overlay.remove();


        // Restore chunks modal
        if (
            chunksWasVisible &&
            chunksModal
        ) {

            chunksModal.classList.remove(
                "hidden"
            );

        }


        // Restore settings modal
        if (
            settingsWasVisible &&
            settingsModal
        ) {

            settingsModal.classList.remove(
                "hidden"
            );

        }


        document.removeEventListener(
            "keydown",
            escHandler
        );

    }


    // ==================================================
    // ESC
    // ==================================================

    function escHandler(event) {

        if (
            event.key === "Escape"
        ) {

            closeModal();

        }

    }


    document.addEventListener(
        "keydown",
        escHandler
    );


    // ==================================================
    // CLOSE BUTTONS
    // ==================================================

    closeButton.addEventListener(
        "click",
        closeModal
    );


    cancelButton.addEventListener(
        "click",
        closeModal
    );


    // ==================================================
    // CLICK OUTSIDE
    // ==================================================

    overlay.addEventListener(
        "click",
        function (event) {

            if (
                event.target === overlay
            ) {

                closeModal();

            }

        }
    );


    // ==================================================
    // SAVE
    // ==================================================

    saveButton.addEventListener(
        "click",
        async function () {

            const newText =
                textarea.value;


            if (
                !newText.trim()
            ) {

                alert(
                    "Text chunk tidak boleh kosong."
                );

                textarea.focus();

                return;

            }


            saveButton.disabled =
                true;

            saveButton.textContent =
                "Saving...";


            try {

                const response =
                    await fetch(
                        "/api/documents/chunk",
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                filename:
                                    filename,

                                chunk_id:
                                    chunkId,

                                new_text:
                                    newText

                            })

                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok
                ) {

                    throw new Error(
                        data.detail ||
                        `Edit chunk error: ${response.status}`
                    );

                }


                closeModal();


                alert(
                    "Chunk berhasil di-update."
                );


                await loadDocumentChunks(
                    filename
                );

            }

            catch (error) {

                console.error(
                    "Edit chunk error:",
                    error
                );


                alert(
                    `Gagal meng-update chunk:\n\n${error.message}`
                );


                saveButton.disabled =
                    false;

                saveButton.textContent =
                    "Save Changes";

            }

        }
    );

}







const settingsUploadButton =
    document.getElementById(
        "settings-upload-button"
    );

const settingsFileInput =
    document.getElementById(
        "settings-file-input"
    );

const settingsUploadStatus =
    document.getElementById(
        "settings-upload-status"
    );

    if (settingsUploadButton) {

    settingsUploadButton.addEventListener(
        "click",
        function () {

            settingsFileInput.click();

        }
    );

}

if (settingsFileInput) {

    settingsFileInput.addEventListener(
        "change",
        async function () {

            if (!this.files || !this.files.length) {
                return;
            }

            const file = this.files[0];

            await uploadDocumentFromSettings(
                file
            );

            this.value = "";

        }
    );

}


async function uploadDocumentFromSettings(file) {

    try {

        settingsUploadButton.disabled = true;

        settingsUploadStatus.classList.remove(
            "hidden"
        );

        settingsUploadStatus.textContent =
            "Uploading and processing document...";


        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        const response =
            await fetch(
                "/api/documents/upload",
                {
                    method: "POST",
                    body: formData
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            if (response.status === 409) {

                throw new Error(
                    "Document already exists."
                );

            }

            throw new Error(
                result.detail ||
                "Upload failed."
            );

        }


        settingsUploadStatus.textContent =
            "Document uploaded successfully.";


        await loadDocuments();


        setTimeout(
            function () {

                settingsUploadStatus.textContent =
                    "";

                settingsUploadStatus.classList.add(
                    "hidden"
                );

            },
            3000
        );


    }
    catch (error) {

        console.error(
            "Upload document error:",
            error
        );


        settingsUploadStatus.textContent =
            "Upload failed: " +
            error.message;


        settingsUploadStatus.classList.remove(
            "hidden"
        );


        setTimeout(
            function () {

                settingsUploadStatus.textContent =
                    "";

                settingsUploadStatus.classList.add(
                    "hidden"
                );

            },
            3000
        );

    }
    finally {

        settingsUploadButton.disabled =
            false;

    }

}