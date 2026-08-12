from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.rag_instance import rag

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    try:

        result = rag.add_document(file)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )