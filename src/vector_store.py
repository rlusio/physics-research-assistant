import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="physics_documents",
    configuration={"hnsw": {"space": "cosine"}}
)


def document_exists(collection, document_id):
    results = collection.get(
        where={"document_id": document_id},
        limit=1
    )

    return len(results["ids"]) > 0

def delete_document(collection, document_id):
    results = collection.get(
        where={"document_id": document_id}
    )

    if results["ids"]:
        collection.delete(ids=results["ids"])

def add_chunks(collection, chunks, embeddings, document_id):
    if len(chunks) != len(embeddings):
        raise ValueError(
            "Liczba fragmentów i embeddingów musi być taka sama"
        )

    if not chunks:
        return

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        record_id = f"{document_id}_{chunk['chunk_id']}"

        ids.append(record_id)
        documents.append(chunk["text"])

        metadata = {
            "document_id": document_id,
            "document": chunk["document"],
            "page": chunk["page"],
            "chunk_id": chunk["chunk_id"]
        }

        metadatas.append(metadata)

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )