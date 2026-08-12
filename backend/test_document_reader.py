from backend.services.document_reader import DocumentReader

reader = DocumentReader()

documents = reader.load_documents("storage/documents")

print("=" * 70)

print("EVE DOCUMENT READER")

print("=" * 70)

for doc in documents:

    print()

    print("Nama File :", doc["filename"])

    print("Tipe      :", doc["type"])

    print("Panjang   :", len(doc["content"]), "karakter")

    print()

    print(doc["content"][:500])

    print("-" * 70)