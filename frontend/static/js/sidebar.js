/* ======================================================
   MAIA SIDEBAR
   Sprint 2.3 Stable
====================================================== */

console.log("MAIA Sidebar Sprint 2.3 Loaded");

const historyContainer = document.getElementById("chat-history");
const newChatButton = document.getElementById("new-chat-btn");
const searchInput = document.getElementById("search-chat");

let popupMenu = null;
let conversations = [];
let activeConversationId = null;

/* ======================================================
   INIT
====================================================== */

document.addEventListener("DOMContentLoaded", () => {

    bindEvents();

    loadConversations();

});

/* ======================================================
   EVENTS
====================================================== */

function bindEvents() {

    if (newChatButton) {

        newChatButton.addEventListener(
            "click",
            createNewChat
        );

    }

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterConversation
        );

    }

    document.addEventListener(
        "click",
        function (e) {

            if (
                popupMenu &&
                !popupMenu.contains(e.target) &&
                !e.target.classList.contains("menu-button")
            ) {

                closePopup();

            }

        }
    );

}

/* ======================================================
   NEW CHAT
====================================================== */

async function createNewChat() {

    try {

        const response = await fetch(
            "/api/new-chat",
            {
                method: "POST"
            }
        );

        if (!response.ok) {

            throw new Error("Create chat gagal");

        }

        const data = await response.json();

        activeConversationId =
            data.conversation_id;

        window.currentConversationId =
            data.conversation_id;

        const chatBox =
            document.getElementById("chat-box");

        if (chatBox) {

            chatBox.innerHTML = "";

        }

        loadConversations();

        const input =
            document.getElementById("question");

        if (input) {

            input.focus();

        }

    }

    catch (err) {

        console.error(err);

        alert("Gagal membuat chat baru.");

    }

}

/* ======================================================
   LOAD HISTORY
====================================================== */

async function loadConversations() {

    try {

        const response =
            await fetch("/api/conversations");

        const data =
            await response.json();

        conversations =
            data.conversations || [];

        renderConversation(conversations);

    }

    catch (err) {

        console.error(err);

    }

}

/* ======================================================
   RENDER HISTORY
====================================================== */

function renderConversation(list) {

    historyContainer.innerHTML = "";

    list.forEach(chat => {

        const row =
            document.createElement("div");

        row.className = "history-row";

        if (chat.id === activeConversationId) {

            row.classList.add("active");

        }

        const title =
            document.createElement("div");

        title.className =
            "history-text";

        title.textContent =
            "💬 " + chat.title;

        title.onclick =
            function () {

                openConversation(chat.id);

            };

        const button =
            document.createElement("button");

        button.className =
            "menu-button";

        button.innerHTML = "⋮";

        button.onclick =
            function (event) {

                event.preventDefault();

                event.stopPropagation();

                showPopupMenu(
                    event,
                    chat.id
                );

            };

        row.appendChild(title);

        row.appendChild(button);

        historyContainer.appendChild(row);

    });

}

/* ======================================================
   SEARCH
====================================================== */

function filterConversation() {

    const keyword =
        searchInput.value
            .toLowerCase()
            .trim();

    const filtered =
        conversations.filter(chat =>
            chat.title
                .toLowerCase()
                .includes(keyword)
        );

    renderConversation(filtered);

}

/* ======================================================
   POPUP MENU
====================================================== */

function showPopupMenu(
    event,
    conversationId
) {

    closePopup();

    popupMenu =
        document.createElement("div");

    popupMenu.className =
        "menu-popup";

    const deleteItem =
        document.createElement("div");

    deleteItem.className =
        "menu-delete";

    deleteItem.textContent =
        "🗑 Delete";

    popupMenu.appendChild(deleteItem);

    document.body.appendChild(popupMenu);

    const rect =
        event.currentTarget.getBoundingClientRect();

    const popupWidth =
        popupMenu.offsetWidth || 160;

    const popupHeight =
        popupMenu.offsetHeight || 44;

    let left =
        rect.right - popupWidth;

    let top =
        rect.bottom + 6;

    if (left < 10) {

        left = 10;

    }

    if (
        left + popupWidth >
        window.innerWidth - 10
    ) {

        left =
            window.innerWidth -
            popupWidth -
            10;

    }

    if (
        top + popupHeight >
        window.innerHeight - 10
    ) {

        top =
            rect.top -
            popupHeight -
            6;

    }

    popupMenu.style.left =
        left + "px";

    popupMenu.style.top =
        top + "px";

    deleteItem.onclick =
        function (e) {

            e.stopPropagation();

            deleteConversation(
                conversationId
            );

        };

}

/* ======================================================
   CLOSE POPUP
====================================================== */

function closePopup() {

    if (popupMenu) {

        popupMenu.remove();

        popupMenu = null;

    }

}

/* ======================================================
   DELETE
====================================================== */

async function deleteConversation(id) {

    if (
        !confirm(
            "Hapus percakapan ini?"
        )
    ) {

        return;

    }

    try {

        const response =
            await fetch(
                `/api/conversation/${id}`,
                {
                    method: "DELETE"
                }
            );

        if (!response.ok) {

            throw new Error();

        }

        closePopup();

        if (
            activeConversationId === id
        ) {

            activeConversationId =
                null;

            const chatBox =
                document.getElementById("chat-box");

            if (chatBox) {

                chatBox.innerHTML = "";

            }

        }

        loadConversations();

    }

    catch (err) {

        console.error(err);

        alert("Delete gagal.");

    }

}

/* ======================================================
   OPEN CHAT
====================================================== */

async function openConversation(id) {

    try {

        activeConversationId = id;

        window.currentConversationId = id;

        loadConversations();

        const response =
            await fetch(
                `/api/history/${id}`
            );

        const data =
            await response.json();

        const chatBox =
            document.getElementById("chat-box");

        if (!chatBox) {

            return;

        }

        chatBox.innerHTML = "";

        data.messages.forEach(msg => {

            if (msg.role === "user") {

                addUserMessage(
                    msg.content
                );

            }

            else {

                addAIMessage(
                    msg.content
                );

            }

        });

    }

    catch (err) {

        console.error(err);

    }

}