from backend.services.rag_service import RAGService


def main():

    rag = RAGService()

    print("=" * 60)
    print("EVE RAG TEST")
    print("=" * 60)

    while True:

        question = input("\nPertanyaan : ")

        if question.lower() in ["exit", "quit"]:

            break

        result = rag.ask(question)

        print()
        print("=" * 60)
        print("JAWABAN")
        print("=" * 60)

        print(result["answer"])

        print()
        print("=" * 60)
        print("SUMBER")
        print("=" * 60)

        for item in result["sources"]:

            print(
                f"Chunk {item['chunk_id']} | Score {item['score']:.3f}"
            )


if __name__ == "__main__":

    main()