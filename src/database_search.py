from vector_store import collection
from embeddings import generate_embeddings

def search_database(query, top_k=3):
    if not query.strip() or top_k <= 0:
        return []
    
    if collection.count() == 0:
        return []

    query_embedding = generate_embeddings([query])[0]
    
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    results_dict = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        results_dict.append({
            "text": text,
            "document": metadata["document"],
            "page": metadata["page"],
            "distance": distance
        })

    return results_dict

