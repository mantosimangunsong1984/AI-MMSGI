from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        print("=" * 60)
        print("MAIA EMBEDDING SERVICE")
        print("=" * 60)
        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Embedding model berhasil di-load.\n")

    def embed(self, text: str):

        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def embed_documents(self, chunks):

        embeddings = []

        for chunk in chunks:

            vector = self.embed(chunk["text"])

            embeddings.append({
                "chunk_id": chunk["chunk_id"],
                "start": chunk["start"],
                "end": chunk["end"],
                "text": chunk["text"],
                "embedding": vector
            })

        return embeddings