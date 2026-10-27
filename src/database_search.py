
import re
import unicodedata

from vector_store import collection
from embeddings import generate_embeddings


STOP_WORDS = {
    "na", "czym", "co", "jak", "jest", "to", "w", "z",
    "do", "i", "o", "czy", "sie", "ten", "ta", "te"
}


def tokenize(text):
    text = text.lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    words = re.findall(r"[a-z0-9]+", text)

    return {
        word[:6] for word in words
        if len(word) >= 5 and word not in STOP_WORDS
    }


def search_database(query, top_k=3):
    if not query.strip() or top_k <= 0:
        return []

    count = collection.count()

    if count == 0:
        return []

    query_embedding = generate_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"]
    )

    semantic_matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        semantic_matches.append({
            "text": text,
            "document": metadata["document"],
            "page": metadata["page"],
            "distance": distance
        })

    # 2. Proste wyszukiwanie słów kluczowych
    query_words = tokenize(query)

    data = collection.get(
        include=["documents", "metadatas"]
    )

    keyword_matches = []

    for text, metadata in zip(
        data["documents"],
        data["metadatas"]
    ):
        text_words = tokenize(text)
        score = len(query_words & text_words)

        if score >= 2:
            keyword_matches.append((
                score,
                {
                    "text": text,
                    "document": metadata["document"],
                    "page": metadata["page"],
                    "distance": None
                }
            ))

    keyword_matches.sort(key=lambda item: item[0], reverse=True)

    # 3. Łączenie wyników bez duplikatów
    combined = []
    seen = set()

    for match in (
        [item[1] for item in keyword_matches]
        + semantic_matches
    ):
        key = (match["document"], match["page"], match["text"])

        if key not in seen:
            seen.add(key)
            combined.append(match)

        if len(combined) >= top_k:
            break

    return combined
