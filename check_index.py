import pickle
import faiss

# ==========================================
# 1. CEK METADATA
# ==========================================

metadata_path = "storage/embeddings/metadata.pkl"

print("=" * 80)
print("CHECK METADATA")
print("=" * 80)

try:
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    print("Metadata count:", len(metadata))

    print("\nDaftar document + chunk:")
    for i, item in enumerate(metadata):
        print(
            i,
            "|",
            item.get("document_name"),
            "| Chunk:",
            item.get("chunk_id")
        )

except Exception as e:
    print("ERROR METADATA:", e)


# ==========================================
# 2. CEK FAISS
# ==========================================

index_path = "storage/embeddings/maia.index"

print("\n" + "=" * 80)
print("CHECK FAISS")
print("=" * 80)

try:
    index = faiss.read_index(index_path)

    print("FAISS vectors:", index.ntotal)
    print("FAISS dimension:", index.d)

except Exception as e:
    print("ERROR FAISS:", e)


# ==========================================
# 3. CEK DOKUMEN KACAMATA
# ==========================================

print("\n" + "=" * 80)
print("CHECK KACAMATA DOCUMENT")
print("=" * 80)

try:
    found = False

    for i, item in enumerate(metadata):

        document_name = item.get("document_name", "")

        if "kacamata" in document_name.lower():

            found = True

            print("\nINDEX :", i)
            print("DOCUMENT :", document_name)
            print("CHUNK :", item.get("chunk_id"))
            print("TEXT :")
            print(item.get("text", ""))
            print("-" * 80)

    if not found:
        print("DOKUMEN KACAMATA TIDAK DITEMUKAN!")

except Exception as e:
    print("ERROR CHECK KACAMATA:", e)