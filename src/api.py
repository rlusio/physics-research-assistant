from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from rag_pipeline import generate_answer
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
import traceback
from pdf_reader import extract_pages
from chunking import split_pages
from embeddings import generate_embeddings
from vector_store import collection, add_chunks

app = FastAPI(title="Physics Research Assistant")

class QuestionRequest(BaseModel):
    question: str =  Field(min_length=2, description="Zadaj pytanie")

    @field_validator("question")
    def validate_question(cls, value: str):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Pytanie musi zawierać co najmniej 2 znaki.")

        return value

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question
    answer = generate_answer(question)

    return {"answer": answer}

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    # 1. Walidacja nazwy pliku
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Dozwolone są tylko pliki PDF."
        )

    # 2. Odczyt pliku z limitem 10 MB
    max_size = 10 * 1024 * 1024
    content = file.file.read(max_size + 1)

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail="Plik przekracza 10 MB."
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Niepoprawny format PDF."
        )

    # 3. Przygotowanie folderu
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.pdf"
    file_path = data_dir / filename

    # 4. Zapis na dysku
    file_path.write_bytes(content)

    try:
        # 5. Odczyt PDF
        pages = extract_pages(str(file_path))

        # 6. Podział na fragmenty
        chunks = split_pages(pages, filename)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Nie udało się wydobyć tekstu z PDF."
            )

        # 7. Przygotowanie tekstów
        texts = [chunk["text"] for chunk in chunks]

        # 8. Generowanie embeddingów
        embeddings = generate_embeddings(texts)

        # 9. Zapis do ChromaDB
        add_chunks(collection, chunks, embeddings)

    except Exception as exc:
        traceback.print_exc()

        file_path.unlink(missing_ok=True)

        if isinstance(exc, HTTPException):
            raise

        raise HTTPException(
            status_code=500,
            detail="Nie udało się przetworzyć dokumentu."
        ) from exc

    return {
        "message": "Dokument został przetworzony",
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "success"
    }