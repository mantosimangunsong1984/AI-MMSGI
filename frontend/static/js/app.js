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


    wrapper.appendChild(bubble);

    chatBox.appendChild(wrapper);


    chatBox.scrollTop =
        chatBox.scrollHeight;

}


// ======================================================
// Create New Chat From Input
// ======================================================

// async function createChatFromInput() {

//     const response =
//         await fetch(
//             "/api/new-chat",
//             {
//                 method: "POST"
//             }
//         );


//     if (!response.ok) {

//         throw new Error(
//             "Gagal membuat conversation baru"
//         );

//     }


//     const data =
//         await response.json();


//     window.currentConversationId =
//         data.conversation_id;


//     localStorage.setItem(
//         "eve_current_conversation",
//         data.conversation_id
//     );


//     chatBox.innerHTML =
//         "";


//     console.log(
//         "New Conversation:",
//         window.currentConversationId
//     );

// }


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