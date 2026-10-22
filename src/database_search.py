from vector_store import collection
from embeddings import model
print("Rekordy widoczne w database_search:", collection.count())

def search_database(query, top_k=3):
    if not query.strip() or top_k <= 0:
        return []

    query_embedding = model.encode(query)

    if collection.count() == 0:
        return []
    
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


if __name__ == "__main__":
    print("Rekordy w bazie:", collection.count())

    query = "Jak obliczyć prędkość chwilową?"
    results = search_database(query)

    if results:
        for result in results:
            print(f"\nDokument: {result['document']}")
            print(f"Strona PDF: {result['page']}")
            print(f"Odległość: {result['distance']:.4f}")
            print(result["text"][:500])
            print("-" * 60)
    else:
        print("Brak wyników.")
