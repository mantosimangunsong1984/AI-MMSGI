from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker
from backend.services.embedding import EmbeddingService

reader = DocumentReader()
chunker = DocumentChunker()
embedder = EmbeddingService()

documents = reader.load_documents("storage/documents")

document = documents[0]

chunks = chunker.split_text(document["content"])

embeddings = embedder.embed_documents(chunks)

print("=" * 60)

print(document["filename"])

print("Jumlah Chunk :", len(chunks))

print("Dimensi Vector :", len(embeddings[0]["embedding"]))

print()

print("5 nilai pertama:")

print(embeddings[0]["embedding"][:5])