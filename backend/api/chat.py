from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.rag_instance import rag
from backend.services.chat_history import ChatHistoryService

router = APIRouter()


# ======================================================
# Load Service sekali saat aplikasi dijalankan
# ======================================================

chat_history = ChatHistoryService()


# ======================================================
# Request & Response Model
# ======================================================

class ChatRequest(BaseModel):
    message: str

class RenameRequest(BaseModel):
    title: str


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str


# ======================================================
# Create New Chat
# ======================================================

@router.post("/new-chat")
async def new_chat():

    conversation_id = chat_history.create_conversation()

    return {
        "conversation_id": conversation_id
    }


# ======================================================
# Chat With Conversation History
# ======================================================

@router.post(
    "/chat/{conversation_id}",
    response_model=ChatResponse
)
async def chat(
    conversation_id: int,
    request: ChatRequest
):

    print("=" * 60)
    print("CONVERSATION ID")
    print(conversation_id)

    print()
    print("PERTANYAAN")
    print(request.message)
    print("=" * 60)


    # ==================================================
    # Pastikan Conversation Ada
    # ==================================================

    conversation = chat_history.get_conversation(
        conversation_id
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation tidak ditemukan."
        )


    # ==================================================
    # Simpan Pertanyaan User
    # ==================================================

    chat_history.save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )


    # ==================================================
    # Kirim ke AI
    # ==================================================

    result = rag.ask(
        request.message,
        top_k=3
    )
    answer = result["answer"]


    print()
    print("JAWABAN")
    print(answer)
    print()


    # ==================================================
    # Simpan Jawaban AI
    # ==================================================

    chat_history.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )


    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer
    )


# ======================================================
# Get Chat History
# ======================================================

@router.get("/history/{conversation_id}")
async def history(
    conversation_id: int
):

    messages = chat_history.get_history(
        conversation_id
    )

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }


# ======================================================
# Get All Conversations
# ======================================================

@router.get("/conversations")
async def conversations():

    data = chat_history.get_conversations()

    return {
        "conversations": data
    }


# ======================================================
# Delete Conversation
# ======================================================

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: int
):

    conversation = chat_history.get_conversation(
        conversation_id
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation tidak ditemukan."
        )


    chat_history.delete_conversation(
        conversation_id
    )

    return {
        "success": True,
        "message": "Conversation berhasil dihapus."
    }

# ======================================================
# Rename Conversation
# ======================================================

@router.put("/conversation/{conversation_id}")
async def rename_conversation(
    conversation_id: int,
    request: RenameRequest
):

    conversation = chat_history.get_conversation(
        conversation_id
    )


    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation tidak ditemukan."
        )


    title = request.title.strip()


    if title == "":

        raise HTTPException(
            status_code=400,
            detail="Title tidak boleh kosong."
        )


    chat_history.update_title(
        conversation_id,
        title
    )


    return {
        "success": True,
        "message": "Conversation berhasil diubah.",
        "title": title
    }