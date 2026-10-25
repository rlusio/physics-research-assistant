from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator
from rag_pipeline import generate_answer
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
import logging
from pdf_reader import extract_pages
from chunking import split_pages
from embeddings import generate_embeddings
from vector_store import collection, add_chunks, document_exists, delete_document
import hashlib

logger = logging.getLogger(__name__)
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
    return generate_answer(request.question)

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Dozwolone są tylko pliki PDF."
        )
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
    
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    document_id = hashlib.sha256(content).hexdigest()
    file_path = data_dir / f"{document_id}.pdf"

    if document_exists(collection, document_id):
        return {
            "message": "Ten dokument został już zaindeksowany.",
            "document_id": document_id,
            "status": "already_exists"
        }

    try:
        file_path.write_bytes(content)  
        pages = extract_pages(str(file_path))
        chunks = split_pages(pages, file.filename)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Nie udało się wydobyć tekstu z PDF."
            )
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = generate_embeddings(texts)
        add_chunks(collection, chunks, embeddings, document_id)

    except Exception as exc:
        logger.exception("Błąd podczas przetwarzania PDF: %s", document_id)

        try:
            delete_document(collection, document_id)
        except Exception:
            logger.exception(
                "Nie udało się wyczyścić dokumentu z ChromaDB: %s",
                document_id
            )
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
        "document_id": document_id,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "success"
    }