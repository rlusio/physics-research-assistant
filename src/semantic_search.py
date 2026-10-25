from sentence_transformers import util
from embeddings import model, generate_embeddings

def search_similar_chunks(query, chunks, embeddings, top_k=3):
    if not chunks:
        return []

    if top_k <= 0:
        return []

    query_embedding = model.encode(query)
    similarities = util.cos_sim(query_embedding, embeddings)[0]

    wartosci = similarities.tolist()
    pairs = enumerate(wartosci)

    pairs_sorted = sorted(
        pairs,
        key=lambda para: para[1],
        reverse=True
    )

    best = pairs_sorted[:top_k]

    results = []

    for index, score in best:
        results.append({
            "chunk_id": index,
            "text": chunks[index],
            "score": score
        })

    return results
