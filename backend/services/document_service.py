from pathlib import Path
import shutil

from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker
from backend.services.embedding import EmbeddingService
from backend.services.vector_store import VectorStore


class DocumentService:

    def __init__(self):

        self.upload_folder = Path("storage/documents")
        self.upload_folder.mkdir(parents=True, exist_ok=True)

        self.reader = DocumentReader()
        self.chunker = DocumentChunker()
        self.embedding = EmbeddingService()

        self.vector_store = VectorStore()

        # Load vector lama jika ada
        self.vector_store.load()

    def upload_document(self, file):

        filename = file.filename

        extension = Path(filename).suffix.lower()

        if extension not in [".pdf", ".docx", ".txt"]:

            raise Exception("Format file tidak didukung.")

        save_path = self.upload_folder / filename

        with open(save_path, "wb") as buffer:

            shutil.copyfileobj(file.file, buffer)

        # ==========================================
        # READ DOCUMENT
        # ==========================================

        if extension == ".pdf":

            text = self.reader.read_pdf(save_path)

        elif extension == ".docx":

            text = self.reader.read_docx(save_path)

        else:

            text = self.reader.read_txt(save_path)

        # ==========================================
        # CHUNKING
        # ==========================================

        chunks = self.chunker.split_text(text)

        # ==========================================
        # EMBEDDING
        # ==========================================

        embeddings = self.embedding.embed_documents(chunks)

        # ==========================================
        # SAVE VECTOR
        # ==========================================

        self.vector_store.add(embeddings)

        self.vector_store.save()

        return {

            "filename": filename,
            "chunks": len(chunks),
            "status": "SUCCESS"

        }