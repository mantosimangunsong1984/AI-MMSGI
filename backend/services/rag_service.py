from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker
from backend.services.embedding import EmbeddingService
from backend.services.vector_store import VectorStore
from backend.ai.engine import AIEngine


class RAGService:

    def __init__(self):

        self.reader = DocumentReader()
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingService()
        self.ai = AIEngine()
        self.store = VectorStore()

        # self.load_documents()

        if not self.store.load():

            self.load_documents()

            self.store.save()

    def load_documents(self):

        print("=" * 60)
        print("LOADING DOCUMENTS")
        print("=" * 60)

        documents = self.reader.load_documents("storage/documents")

        total_chunk = 0

        for document in documents:

            chunks = self.chunker.split_text(
                document["content"]
            )

            embeddings = self.embedder.embed_documents(
                chunks
            )

            self.store.add(embeddings)

            total_chunk += len(chunks)

            print(
                f"{document['filename']} -> {len(chunks)} chunk"
            )

        print()
        print(f"Total Chunk : {total_chunk}")
        print()

    def search(self, question, top_k=3):

        query_vector = self.embedder.embed(question)

        return self.store.search(
            query_vector,
            top_k
        )

    def ask(self, question, top_k=3):

        results = self.search(
            question,
            top_k
        )

        context = ""

        for item in results:

            context += item["text"]
            context += "\n\n"

        answer = self.ai.chat_with_context(
            context=context,
            question=question
        )

        return {
            "answer": answer,
            "sources": results
        }