let currentConversationId = null;


const sendButton = document.getElementById("send-btn");
const input = document.getElementById("question");
const chatBox = document.getElementById("chat-box");


sendButton.addEventListener("click", sendMessage);


input.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});


// ======================================================
// UI Message
// ======================================================

function addUserMessage(message) {

    const wrapper = document.createElement("div");

    wrapper.className = "user-message";


    const bubble = document.createElement("div");

    bubble.className = "bubble-user";

    bubble.textContent = message;


    wrapper.appendChild(bubble);

    chatBox.appendChild(wrapper);


    chatBox.scrollTop = chatBox.scrollHeight;

}



function addAIMessage(message) {


    const wrapper = document.createElement("div");

    wrapper.className = "ai-message";


    const bubble = document.createElement("div");

    bubble.className = "bubble-ai";

    bubble.textContent = message;


    wrapper.appendChild(bubble);

    chatBox.appendChild(wrapper);


    chatBox.scrollTop = chatBox.scrollHeight;

}



// ======================================================
// Create New Chat
// ======================================================

async function createChatFromInput() {


    const response = await fetch(
        "/api/new-chat",
        {
            method: "POST"
        }
    );


    const data = await response.json();


    currentConversationId = data.conversation_id;


    chatBox.innerHTML = "";


    console.log(
        "New Conversation:",
        currentConversationId
    );

}



// ======================================================
// Send Message
// ======================================================

async function sendMessage() {


    const message = input.value.trim();


    if (message === "") {
        return;
    }


    // Jika belum ada chat
    // otomatis buat conversation baru

    if (currentConversationId === null) {

        // await createNewChat();
        await createChatFromInput();

    }



    addUserMessage(message);


    input.value = "";



    const loadingId =
        "loading-" + Date.now();



    chatBox.innerHTML += `

    <div id="${loadingId}" class="ai-message">

        <div class="bubble-ai">

            ⏳ MAIA sedang berpikir...

        </div>

    </div>

    `;



    try {


        const response = await fetch(

            `/api/chat/${currentConversationId}`,

            {

                method: "POST",

                headers: {

                    "Content-Type":
                    "application/json"

                },


                body: JSON.stringify({

                    message: message

                })

            }

        );



        const data = await response.json();



        document
        .getElementById(loadingId)
        .remove();



        addAIMessage(
            data.answer
        );



    }


    catch(error) {


        document
        .getElementById(loadingId)
        ?.remove();



        addAIMessage(
            "Gagal menghubungi MAIA."
        );


        console.error(error);

    }

}



// ======================================================
// Welcome Screen
// ======================================================

function hideWelcome() {

    const welcome =
    document.querySelector(".welcome");


    if (welcome) {

        welcome.remove();

    }

}