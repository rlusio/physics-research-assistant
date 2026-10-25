import sys
from pathlib import Path
from unittest.mock import patch
import numpy as np

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from fastapi.testclient import TestClient
from api import app

def test_health():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ask_success():
    with patch("api.generate_answer") as mock_generate:
        mock_generate.return_value = {
            "answer": "Energia nie powstaje ani nie ginie.",
            "sources": []
        }

        client = TestClient(app)

        response = client.post(
            "/ask",
            json={"question": "Co mówi pierwsza zasada termodynamiki?"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "answer": "Energia nie powstaje ani nie ginie.",
            "sources": []
        }

        mock_generate.assert_called_once_with(
            "Co mówi pierwsza zasada termodynamiki?"
        )

def test_ask_invalid_question():
    client = TestClient(app)

    response = client.post(
        "/ask",
        json={"question": "   "}
    )

    assert response.status_code == 422

def test_upload_invalid_extension():
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "document.txt",
                b"To jest zwykly plik tekstowy.",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400

def test_upload_invalid_pdf_content():
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "fake.pdf",
                b"To nie jest prawdziwy PDF.",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400

def test_upload_file_too_large():
    client = TestClient(app)

    oversized_content = (
        b"%PDF-" + b"0" * (10 * 1024 * 1024)
    )

    response = client.post(
        "/upload",
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 413

def test_upload_duplicate():
    with patch("api.document_exists", return_value=True) as mock_exists:

        client = TestClient(app)

        response = client.post(
            "/upload",
            files={
                "file": (
                    "physics.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf"
                )
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "already_exists"
        assert "document_id" in response.json()

        mock_exists.assert_called_once()

def test_upload_success():
    pages = [
        {"page": 1, "text": "Pierwsza zasada termodynamiki."}
    ]

    chunks = [
        {
            "document": "physics.pdf",
            "page": 1,
            "chunk_id": 0,
            "text": "Pierwsza zasada termodynamiki."
        }
    ]

    embeddings = np.array([[0.1, 0.2, 0.3]])

    with (
        patch("api.document_exists", return_value=False),
        patch("api.extract_pages", return_value=pages) as mock_extract,
        patch("api.split_pages", return_value=chunks) as mock_split,
        patch("api.generate_embeddings", return_value=embeddings) as mock_embed,
        patch("api.add_chunks") as mock_add,
        patch("api.Path.write_bytes"),
    ):
        client = TestClient(app)

        response = client.post(
            "/upload",
            files={
                "file": (
                    "physics.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf"
                )
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["pages"] == 1
        assert response.json()["chunks"] == 1

        mock_extract.assert_called_once()
        mock_split.assert_called_once_with(pages, "physics.pdf")
        mock_embed.assert_called_once_with(
            ["Pierwsza zasada termodynamiki."]
        )
        mock_add.assert_called_once()

def test_upload_processing_error():
    with (
        patch("api.document_exists", return_value=False),
        patch("api.extract_pages", side_effect=RuntimeError("PDF error")),
        patch("api.delete_document") as mock_delete,
        patch("api.Path.write_bytes"),
        patch("api.Path.unlink") as mock_unlink,
    ):
        client = TestClient(app)

        response = client.post(
            "/upload",
            files={
                "file": (
                    "broken.pdf",
                    b"%PDF-1.4 broken content",
                    "application/pdf"
                )
            }
        )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "Nie udało się przetworzyć dokumentu."
        )

        mock_delete.assert_called_once()
        mock_unlink.assert_called_once_with(missing_ok=True)