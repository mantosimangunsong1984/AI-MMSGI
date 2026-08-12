from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker
from backend.services.embedding import EmbeddingService
from backend.services.vector_store import VectorStore
from backend.ai.engine import AIEngine

from pathlib import Path
import shutil
import numpy as np


class RAGService:

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        print("\n")
        print("=" * 80)
        print("EVE RAG SERVICE")
        print("=" * 80)

        self.reader = DocumentReader()

        self.chunker = DocumentChunker()

        self.embedder = EmbeddingService()

        self.ai = AIEngine()

        self.store = VectorStore(
            dimension=self.embedder.dimension
        )

        # =================================================
        # LOAD EXISTING VECTOR
        # =================================================

        loaded = self.store.load()

        if loaded:

            print(
                "Existing vector store berhasil digunakan."
            )

        else:

            print(
                "MEMBUAT VECTOR BARU..."
            )

            self.load_documents()

            self.store.save()

        print("=" * 80)
        print("EVE RAG SERVICE READY")
        print("=" * 80)
        print()

    # =====================================================
    # LOAD ALL DOCUMENTS
    # =====================================================

    def load_documents(self):

        print("\n")
        print("=" * 80)
        print("LOADING DOCUMENTS")
        print("=" * 80)

        documents = self.reader.load_documents(
            "storage/documents"
        )

        if not documents:

            print(
                "Tidak ada document."
            )

            return

        print(
            "Total document:",
            len(documents)
        )

        total_chunk = 0

        # =================================================
        # PROCESS DOCUMENT
        # =================================================

        for document in documents:

            print("\n")
            print("=" * 80)

            print(
                "DOCUMENT:",
                document["filename"]
            )

            print("=" * 80)

            content = document.get(
                "content",
                ""
            )

            print(
                "Content length:",
                len(content)
            )

            # =============================================
            # CHUNK
            # =============================================

            chunks = self.chunker.split_text(
                document
            )

            if not chunks:

                print(
                    "Tidak ada chunk."
                )

                continue

            print(
                "Jumlah chunk:",
                len(chunks)
            )

            # =============================================
            # DEBUG CHUNK
            # =============================================

            for chunk in chunks:

                print("\n")
                print("-" * 80)

                print(
                    "Document :",
                    chunk["document_name"]
                )

                print(
                    "Chunk    :",
                    chunk["chunk_id"]
                )

                print(
                    "Text:"
                )

                print(
                    chunk["text"]
                )

                print("-" * 80)

            # =============================================
            # EMBEDDING
            # =============================================

            embeddings = (
                self.embedder.embed_documents(
                    chunks
                )
            )

            # =============================================
            # ADD VECTOR
            # =============================================

            self.store.add(
                embeddings
            )

            total_chunk += len(
                chunks
            )

            print(
                f"{document['filename']} "
                f"-> {len(chunks)} chunk"
            )

        print("\n")
        print("=" * 80)
        print("DOCUMENT LOADING SELESAI")
        print("=" * 80)

        print(
            "Total Document:",
            len(documents)
        )

        print(
            "Total Chunk:",
            total_chunk
        )

        print(
            "Total Vector:",
            self.store.index.ntotal
        )

        print("=" * 80)

    # =====================================================
    # ADD SINGLE DOCUMENT
    # =====================================================

    def add_document(self, file):

        filename = file.filename

        extension = Path(
            filename
        ).suffix.lower()

        print("\n")
        print("=" * 80)
        print("ADD DOCUMENT")
        print("=" * 80)

        print(
            "Filename:",
            filename
        )

        print(
            "Extension:",
            extension
        )

        # =================================================
        # VALIDATE EXTENSION
        # =================================================

        if extension not in [
            ".pdf",
            ".docx",
            ".txt"
        ]:

            raise Exception(
                "Format file tidak didukung. "
                "Gunakan PDF, DOCX, atau TXT."
            )

        # =================================================
        # SAVE DOCUMENT
        # =================================================

        save_folder = Path(
            "storage/documents"
        )

        save_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        save_path = (
            save_folder /
            filename
        )

        with open(
            save_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(
            "File disimpan:",
            save_path
        )

        # =================================================
        # READ DOCUMENT
        # =================================================

        if extension == ".pdf":

            text = self.reader.read_pdf(
                save_path
            )

        elif extension == ".docx":

            text = self.reader.read_docx(
                save_path
            )

        else:

            text = self.reader.read_txt(
                save_path
            )

        print(
            "Content length:",
            len(text)
        )

        if not text.strip():

            raise Exception(
                "Dokumen tidak memiliki text "
                "yang dapat diproses."
            )

        # =================================================
        # DOCUMENT OBJECT
        # =================================================

        document = {

            "filename":
                filename,

            "document_name":
                Path(filename).stem,

            "extension":
                extension,

            "size":
                save_path.stat().st_size,

            "content":
                text

        }

        # =================================================
        # CHUNK
        # =================================================

        chunks = self.chunker.split_text(
            document
        )

        if not chunks:

            raise Exception(
                "Dokumen berhasil dibaca, "
                "tetapi tidak menghasilkan chunk."
            )

        print(
            "Jumlah chunk:",
            len(chunks)
        )

        # =================================================
        # DEBUG CHUNK
        # =================================================

        for chunk in chunks:

            print("\n")
            print("-" * 80)

            print(
                "Document:",
                chunk["document_name"]
            )

            print(
                "Chunk:",
                chunk["chunk_id"]
            )

            print(
                chunk["text"]
            )

            print("-" * 80)

        # =================================================
        # EMBEDDING
        # =================================================

        embeddings = (
            self.embedder.embed_documents(
                chunks
            )
        )

        # =================================================
        # ADD VECTOR
        # =================================================

        self.store.add(
            embeddings
        )

        # =================================================
        # SAVE VECTOR STORE
        # =================================================

        self.store.save()

        print("=" * 80)
        print("DOCUMENT BERHASIL DITAMBAHKAN")
        print("=" * 80)

        return {

            "filename":
                filename,

            "chunks":
                len(chunks),

            "status":
                "SUCCESS"

        }

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        question,
        top_k=3
    ):

        print("\n")
        print("=" * 80)
        print("RAG SEARCH DEBUG")
        print("=" * 80)

        print(
            "QUESTION:",
            repr(question)
        )

        print(
            "QUESTION LENGTH:",
            len(question)
        )

        # =================================================
        # VALIDATE QUESTION
        # =================================================

        if not question or not question.strip():

            print(
                "Question kosong."
            )

            return []

        # =================================================
        # EMBEDDING QUERY
        # =================================================

        query_vector = (
            self.embedder.embed(
                question
            )
        )

        print(
            "VECTOR SHAPE:",
            query_vector.shape
        )

        print(
            "VECTOR DTYPE:",
            query_vector.dtype
        )

        print(
            "VECTOR NORM:",
            float(
                np.linalg.norm(
                    query_vector
                )
            )
        )

        print(
            "VECTOR FIRST 10:"
        )

        print(
            query_vector[:10]
        )

        # =================================================
        # VECTOR SEARCH
        # =================================================

        results = self.store.search(
            query_vector=query_vector,
            question=question,
            top_k=top_k
        )

        print("\n")
        print("=" * 80)
        print("RAG SEARCH RESULT")
        print("=" * 80)

        print(
            "Total result:",
            len(results)
        )

        for i, item in enumerate(
            results,
            start=1
        ):

            print("\n")
            print(
                f"Result #{i}"
            )

            print(
                "Document:",
                item["document_name"]
            )

            print(
                "Chunk:",
                item["chunk_id"]
            )

            print(
                "Score:",
                item.get(
                    "score"
                )
            )

            print(
                "Raw Score:",
                item.get(
                    "raw_score"
                )
            )

            print(
                "Keyword Boost:",
                item.get(
                    "keyword_boost"
                )
            )

            print(
                "Matched Keywords:",
                item.get(
                    "matched_keywords"
                )
            )

            print(
                "Text:"
            )

            print(
                item["text"][:500]
            )

        print("=" * 80)

        return results

    # =====================================================
    # ASK
    # =====================================================

    def ask(
        self,
        question,
        top_k=3
    ):

        print("\n")
        print("=" * 80)
        print("EVE RAG ASK")
        print("=" * 80)

        print(
            "Question:",
            repr(question)
        )

        # =================================================
        # SEARCH
        # =================================================

        results = self.search(
            question,
            top_k
        )

        # =================================================
        # NO RESULT
        # =================================================

        if not results:

            print("\n")
            print(
                "Tidak ditemukan context "
                "yang cukup relevan."
            )

            return {

                "answer":
                    "Maaf, informasi tersebut "
                    "tidak ditemukan pada dokumen "
                    "yang tersedia.",

                "sources":
                    []

            }

        # =================================================
        # BUILD CONTEXT
        # =================================================

        context_parts = []

        for index, item in enumerate(
            results,
            start=1
        ):

            source_text = (
                f"[SOURCE {index}]\n"
                f"Document: "
                f"{item['document_name']}\n"
                f"Chunk: "
                f"{item['chunk_id']}\n"
                f"Score: "
                f"{item['score']}\n\n"
                f"{item['text']}"
            )

            context_parts.append(
                source_text
            )

        context = "\n\n".join(
            context_parts
        )

        # =================================================
        # DEBUG CONTEXT
        # =================================================

        print("\n")
        print("=" * 80)
        print("CONTEXT YANG DIKIRIM KE AI")
        print("=" * 80)

        print(
            context
        )

        print("=" * 80)

        # =================================================
        # AI
        # =================================================

        answer = (
            self.ai.chat_with_context(
                context=context,
                question=question
            )
        )

        # =================================================
        # RESPONSE
        # =================================================

        print("\n")
        print("=" * 80)
        print("EVE ANSWER")
        print("=" * 80)

        print(
            answer
        )

        print("=" * 80)

        return {

            "answer":
                answer,

            "sources":
                results

        }