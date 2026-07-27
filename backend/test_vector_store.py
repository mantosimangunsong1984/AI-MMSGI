from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker
from backend.services.embedding import EmbeddingService
from backend.services.vector_store import VectorStore

reader = DocumentReader()
chunker = DocumentChunker()
embedder = EmbeddingService()
store = VectorStore()

documents = reader.load_documents("storage/documents")

chunks = chunker.split_text(documents[0]["content"])

embeddings = embedder.embed_documents(chunks)

store.add(embeddings)

question = "Apa tujuan Employee Handbook?"

query_vector = embedder.embed(question)

results = store.search(query_vector)

print("=" * 70)
print("PERTANYAAN")
print(question)
print("=" * 70)

for item in results:

    print()
    print("Score :", round(item["score"], 3))
    print("Chunk :", item["chunk_id"])
    print()
    print(item["text"][:300])
    print("-" * 70)