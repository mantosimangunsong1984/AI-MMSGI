from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Query
)

from backend.core.rag_instance import rag


router = APIRouter()


# ======================================================
# UPLOAD DOCUMENT
# ======================================================

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


# ======================================================
# GET DOCUMENT LIST
# ======================================================

@router.get("/documents")
async def get_documents():

    try:

        documents = rag.get_documents()

        return {
            "documents": documents
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ======================================================
# DELETE DOCUMENT
# ======================================================

@router.delete("/documents")
async def delete_document(
    filename: str = Query(...)
):

    try:

        result = rag.delete_document(
            filename
        )

        return result

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )