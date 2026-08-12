from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:

    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):

        print("=" * 60)
        print("EVE EMBEDDING SERVICE")
        print("=" * 60)

        print("Loading embedding model...")
        print("Model :", self.MODEL_NAME)

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

        self.dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        print(
            "Embedding dimension :",
            self.dimension
        )

        print("Embedding model berhasil di-load.\n")

    # =====================================================
    # SINGLE TEXT EMBEDDING
    # =====================================================

    def embed(self, text: str):

        if text is None:
            text = ""

        text = str(text).strip()

        if not text:
            return np.zeros(
                self.dimension,
                dtype=np.float32
            )

        vector = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return vector.astype(
            np.float32
        )

    # =====================================================
    # BATCH DOCUMENT EMBEDDING
    # =====================================================

    def embed_documents(self, chunks):

        if not chunks:
            return []

        texts = []

        for chunk in chunks:

            text = chunk.get(
                "text",
                ""
            )

            texts.append(
                str(text)
            )

        print(
            f"Generating embeddings for {len(texts)} chunks..."
        )

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        vectors = np.asarray(
            vectors,
            dtype=np.float32
        )

        embeddings = []

        for chunk, vector in zip(
            chunks,
            vectors
        ):

            embeddings.append({

                "filename": chunk[
                    "filename"
                ],

                "document_name": chunk[
                    "document_name"
                ],

                "extension": chunk[
                    "extension"
                ],

                "size": chunk[
                    "size"
                ],

                "chunk_id": chunk[
                    "chunk_id"
                ],

                "text": chunk[
                    "text"
                ],

                "embedding": vector

            })

        print(
            "Embedding berhasil dibuat:",
            len(embeddings),
            "chunks"
        )

        return embeddings