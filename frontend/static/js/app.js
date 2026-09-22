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

if (settingsButton) {

    settingsButton.addEventListener(
        "click",
        function () {

            openSettings();

        }
    );

}


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

async function openSettings() {

    if (!settingsModal) {
        return;
    }

    settingsModal.classList.remove(
        "hidden"
    );

    await loadSettingsModels();

    await loadDocuments();

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

        const response =
            await fetch("/api/documents");


        if (!response.ok) {

            throw new Error(
                `Document API error: ${response.status}`
            );

        }


        const data =
            await response.json();


        const documents =
            data.documents || [];


        // Hapus tulisan Loading documents...
        settingsDocumentList.innerHTML = "";
        

        // Tidak ada dokumen
        if (documents.length === 0) {

            settingsDocumentList.innerHTML = `
                <div class="document-empty">
                    No documents available.
                </div>
            `;

            return;

        }


        settingsDocumentList.innerHTML =
            "";


        documents.forEach(
            function (doc) {

                const row =
                    document.createElement(
                        "div"
                    );

                row.className =
                    "settings-document-item";


                // Document information
                const info =
                    document.createElement(
                        "div"
                    );

                info.className =
                    "document-info";


                const icon =
                    document.createElement(
                        "span"
                    );

                icon.className =
                    "document-icon";

                icon.textContent =
                    "📄";


                const name =
                    document.createElement(
                        "span"
                    );

                name.className =
                    "document-name";

                name.textContent =
                    doc.filename;


                info.appendChild(
                    icon
                );

                info.appendChild(
                    name
                );


                // Delete button
                const deleteButton =
                    document.createElement(
                        "button"
                    );

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

                        <path
                            d="M10 11v6">
                        </path>

                        <path
                            d="M14 11v6">
                        </path>

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


                row.appendChild(
                    info
                );

                row.appendChild(
                    deleteButton
                );


                settingsDocumentList.appendChild(
                    row
                );

            }
        );

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
// DELETE DOCUMENT
// ======================================================

async function deleteDocument(
    filename,
    deleteButton
) {

    const confirmed =
        confirm(
            `Apakah Anda yakin ingin menghapus dokumen:\n\n${filename}\n\nDokumen akan dihapus dari storage dan knowledge base EVE.`
        );


    if (!confirmed) {

        return;

    }


    try {

        deleteButton.disabled =
            true;


        deleteButton.style.opacity =
            "0.5";


        const response =
            await fetch(
                `/api/documents?filename=${encodeURIComponent(filename)}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Delete error: ${response.status}`
            );

        }


        console.log(
            "Document deleted:",
            data
        );


        alert(
            `Dokumen berhasil dihapus:\n${filename}`
        );


        // Refresh document list
        await loadDocuments();

    }

    catch (error) {

        console.error(
            "Delete document error:",
            error
        );


        alert(
            `Gagal menghapus dokumen:\n\n${error.message}`
        );


        deleteButton.disabled =
            false;

        deleteButton.style.opacity =
            "1";

    }

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


async function uploadDocumentFromSettings(
    file
) {

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

                settingsUploadStatus.classList.add(
                    "hidden"
                );

            },
            2000
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

    }
    finally {

        settingsUploadButton.disabled =
            false;

    }

}

