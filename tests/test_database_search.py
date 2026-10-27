
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from database_search import search_database, tokenize


def test_tokenize():
    words = tokenize("Doświadczenie Michelsona-Morleya")

    assert "doswia" in words
    assert "michel" in words
    assert "morley" in words


def test_empty_query():
    assert search_database("   ") == []


def test_invalid_top_k():
    assert search_database("Fizyka", top_k=0) == []


def test_empty_database():
    with patch("database_search.collection") as mock_collection:
        mock_collection.count.return_value = 0

        result = search_database("Co to jest energia?")

    assert result == []


def test_keyword_match_before_semantic():
    with (
        patch("database_search.collection") as mock_collection,
        patch("database_search.generate_embeddings") as mock_embeddings
    ):
        mock_collection.count.return_value = 2
        mock_embeddings.return_value = np.array([[0.1, 0.2]])

        mock_collection.query.return_value = {
            "documents": [["Tekst o pochodnych."]],
            "metadatas": [[{
                "document": "mechanika.pdf",
                "page": 10
            }]],
            "distances": [[0.6]]
        }

        mock_collection.get.return_value = {
            "documents": [
                "Doświadczenie Michelsona-Morleya wykorzystuje interferometr.",
                "Tekst o pochodnych."
            ],
            "metadatas": [
                {"document": "relatywistyka.pdf", "page": 5},
                {"document": "mechanika.pdf", "page": 10}
            ]
        }

        results = search_database(
            "Na czym polega doświadczenie Michelsona-Morleya?",
            top_k=2
        )

    assert len(results) == 2
    assert results[0]["document"] == "relatywistyka.pdf"
    assert results[0]["page"] == 5
    assert results[0]["distance"] is None
    assert results[1]["document"] == "mechanika.pdf"


def test_semantic_fallback():
    with (
        patch("database_search.collection") as mock_collection,
        patch("database_search.generate_embeddings") as mock_embeddings
    ):
        mock_collection.count.return_value = 1
        mock_embeddings.return_value = np.array([[0.1, 0.2]])

        mock_collection.query.return_value = {
            "documents": [["Energia jest zachowana."]],
            "metadatas": [[{
                "document": "fizyka.pdf",
                "page": 3
            }]],
            "distances": [[0.25]]
        }

        mock_collection.get.return_value = {
            "documents": ["Energia jest zachowana."],
            "metadatas": [{
                "document": "fizyka.pdf",
                "page": 3
            }]
        }

        results = search_database(
            "Wyjaśnij zasadę zachowania energii.",
            top_k=1
        )

    assert len(results) == 1
    assert results[0]["document"] == "fizyka.pdf"
    assert results[0]["distance"] == 0.25

