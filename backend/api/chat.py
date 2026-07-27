from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.rag_service import RAGService

router = APIRouter()

# ======================================================
# Load RAG sekali saat aplikasi dijalankan
# ======================================================

rag = RAGService()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str



@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    print("=" * 60)
    print("PERTANYAAN")
    print(request.message)
    print("=" * 60)

    result = rag.ask(request.message)

    print()
    print("JAWABAN")
    print(result["answer"])
    print()

    return ChatResponse(
        answer=result["answer"]
    )


# @router.post(
#     "/chat",
#     response_model=ChatResponse
# )
# async def chat(request: ChatRequest):

#     result = rag.ask(request.message)

#     return ChatResponse(
#         answer=result["answer"]
#     )