from backend.services.document_reader import DocumentReader
from backend.services.chunker import DocumentChunker

reader = DocumentReader()

documents = reader.load_documents("storage/documents")

chunker = DocumentChunker()

for document in documents:

    print("=" * 70)

    print(document["filename"])

    print("=" * 70)

    chunks = chunker.split_text(document["content"])

    print("Jumlah Chunk :", len(chunks))

    print()

    for chunk in chunks[:3]:

        print("-" * 70)
        print("Chunk :", chunk["chunk_id"])
        print("Range :", chunk["start"], "-", chunk["end"])
        print(chunk["text"][:250])
        print()