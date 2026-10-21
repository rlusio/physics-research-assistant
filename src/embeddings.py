from sentence_transformers import SentenceTransformer, util
from chunking import split_text
from pdf_reader import extract_text
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def generate_embeddings(chunks):
    embeddings = model.encode(chunks)
    return embeddings

if __name__ == "__main__":
    text = extract_text("data/materialy01.pdf")
    chunks = split_text(text)

    embeddings = generate_embeddings(chunks)

    print(f"Liczba fragmentów: {len(chunks)}")
    print(f"Kształt macierzy: {embeddings.shape}")