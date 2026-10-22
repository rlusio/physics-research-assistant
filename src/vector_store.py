import hashlib
import chromadb
from pdf_reader import extract_pages
from chunking import split_pages
from embeddings import generate_embeddings


client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="physics_documents",
    configuration={"hnsw": {"space": "cosine"}}
)


def add_chunks(collection, chunks, embeddings):
    if len(chunks) != len(embeddings):
        raise ValueError("Liczba fragmentów i embeddingów musi być taka sama")

    if not chunks:
        return

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        document_id = hashlib.sha256(
            chunk["document"].encode("utf-8")
        ).hexdigest()[:16]

        record_id = f"{document_id}_{chunk['chunk_id']}"

        ids.append(record_id)
        documents.append(chunk["text"])

        metadata = {
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


if __name__ == "__main__":
    pages = extract_pages("data/materialy01.pdf")
    chunks = split_pages(pages, "materialy01.pdf")
    texts = [chunk["text"] for chunk in chunks]

    if texts:
        embeddings = generate_embeddings(texts)
        add_chunks(collection, chunks, embeddings)

    print(f"Liczba rekordów w bazie: {collection.count()}")
