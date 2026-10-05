from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Query
)

from backend.core.rag_instance import rag
from pydantic import BaseModel


router = APIRouter()



class UpdateChunkRequest(BaseModel):

        filename: str

        chunk_id: int

        new_text: str



# ======================================================
# UPDATE CHUNK
# ======================================================

@router.put("/documents/chunk")
async def update_chunk(
    request: UpdateChunkRequest
):

    try:

        result = rag.update_chunk(
            filename=request.filename,
            chunk_id=request.chunk_id,
            new_text=request.new_text
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




@router.delete("/documents/chunk")
async def delete_chunk(
    filename: str = Query(...),
    chunk_id: int = Query(...)
):
    try:
        result = rag.delete_chunk(
            filename=filename,
            chunk_id=chunk_id
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




# ======================================================
# UPLOAD DOCUMENT
# ======================================================

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:

        existing_documents = rag.get_documents()

        existing_filenames = [
            doc["filename"]
            for doc in existing_documents
        ]

        if file.filename in existing_filenames:
            raise HTTPException(
                status_code=409,
                detail=f"Document '{file.filename}' already exists."
            )

        result = rag.add_document(file)

        return result

    except HTTPException:
        raise

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


# ======================================================
# GET DOCUMENT CHUNKS
# ======================================================

@router.get("/documents/chunks")
async def get_document_chunks(
    filename: str = Query(...)
):

    try:

        result = rag.get_chunks(
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


# ======================================================
# GET SINGLE CHUNK
# ======================================================

@router.get("/documents/chunk")
async def get_chunk(
    filename: str = Query(...),
    chunk_id: int = Query(...)
):

    try:

        result = rag.get_chunk(
            filename,
            chunk_id
        )

        return result

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


   