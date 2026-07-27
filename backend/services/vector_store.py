import joblib
from pathlib import Path
from backend.utils.config import (
    VECTOR_INDEX,
    VECTOR_METADATA
)
import faiss
import numpy as np
from pathlib import Path


class VectorStore:

    def __init__(self, dimension=384):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.metadata = []

    def add(self, embeddings):

        vectors = []

        for item in embeddings:

            vectors.append(item["embedding"])

            self.metadata.append({

                "chunk_id": item["chunk_id"],
                "start": item["start"],
                "end": item["end"],
                "text": item["text"]

            })

        vectors = np.array(vectors).astype("float32")

        self.index.add(vectors)

    def search(self, query_vector, top_k=3):

        query = np.array([query_vector]).astype("float32")

        scores, indexes = self.index.search(query, top_k)

        results = []

        for score, idx in zip(scores[0], indexes[0]):

            if idx == -1:
                continue

            item = self.metadata[idx].copy()

            item["score"] = float(score)

            results.append(item)

        return results


    def save(self):

        VECTOR_INDEX.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(VECTOR_INDEX)
        )

        joblib.dump(
            self.metadata,
            VECTOR_METADATA
        )

        print()
        print("Vector index berhasil disimpan.")


    def load(self):

        if not VECTOR_INDEX.exists():

            return False

        self.index = faiss.read_index(
            str(VECTOR_INDEX)
        )

        self.metadata = joblib.load(
            VECTOR_METADATA
        )

        print()
        print("Vector index berhasil dimuat.")

        return True
    

    def is_empty(self):

        return self.index.ntotal == 0