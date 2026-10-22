from sentence_transformers import SentenceTransformer, util
from chunking import split_pages
from pdf_reader import extract_pages

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def generate_embeddings(chunks):
    embeddings = model.encode(chunks)
    return embeddings

if __name__ == "__main__":
    pages = extract_pages("data/materialy01.pdf")
    chunks = split_pages(pages, "materialy01.pdf")
    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)

    print(f"Liczba fragmentów: {len(chunks)}")
    print(f"Kształt macierzy: {embeddings.shape}")