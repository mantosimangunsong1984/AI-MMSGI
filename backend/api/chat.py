from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag_service import RAGService
from backend.services.chat_history import ChatHistoryService


router = APIRouter()


# ======================================================
# Load Service sekali saat aplikasi dijalankan
# ======================================================

rag = RAGService()
chat_history = ChatHistoryService()


# ======================================================
# Request & Response Model
# ======================================================

class ChatRequest(BaseModel):
    message: str


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
    # Simpan pertanyaan user
    # ==================================================

    chat_history.save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )


    # ==================================================
    # Kirim ke RAG + AI Engine
    # ==================================================

    result = rag.ask(
        request.message
    )


    answer = result["answer"]


    print()
    print("JAWABAN")
    print(answer)
    print()



    # ==================================================
    # Simpan jawaban AI
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