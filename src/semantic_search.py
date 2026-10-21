from sentence_transformers import util
from embeddings import model, generate_embeddings
from pdf_reader import extract_text
from chunking import split_text

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

if __name__ == "__main__":
    text = extract_text("data/materialy01.pdf")
    chunks = split_text(text)
    embeddings = generate_embeddings(chunks)

    query = "Jak obliczyć prędkość chwilową ciała?"

    results = search_similar_chunks(query, chunks, embeddings)

    for result in results:
        print(f"\nFragment: {result['chunk_id']}")
        print(f"Similarity: {result['score']:.4f}")
        print(result["text"])
        print("-" * 60)