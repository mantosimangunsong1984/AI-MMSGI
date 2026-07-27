const sendButton = document.getElementById("send-btn");
const input = document.getElementById("question");
const chatBox = document.getElementById("chat-box");

sendButton.addEventListener("click", sendMessage);

input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});


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


async function sendMessage() {

    const message = input.value.trim();

    const loadingId = "loading-" + Date.now();

    chatBox.innerHTML += `
    <div id="${loadingId}" class="ai-message">
        <div class="bubble-ai">
            ⏳ MAIA sedang berpikir...
        </div>
    </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    if (message === "") {
        return;
    }

    // Tampilkan pesan user

    addUserMessage(message);

    input.value = "";

    try {

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();
        document.getElementById(loadingId).remove();

        // Tampilkan jawaban AI
        
        addAIMessage(data.answer);

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {

        chatBox.innerHTML += `
            <div style="color:red;">
                Gagal menghubungi MAIA.
            </div>
        `;

        console.error(error);
    }
}

function hideWelcome() {
    const welcome = document.querySelector(".welcome");
    if (welcome) {
        welcome.remove();
    }
}