import sys
from pathlib import Path
from unittest.mock import MagicMock
import numpy as np
import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from vector_store import document_exists, add_chunks, delete_document


def test_document_exists():
    fake_collection = MagicMock()

    fake_collection.get.return_value = {
        "ids": ["abc123_0"]
    }

    result = document_exists(
        fake_collection,
        document_id="abc123"
    )

    assert result is True

    fake_collection.get.assert_called_once_with(
        where={"document_id": "abc123"},
        limit=1
    )

def test_document_not_exists():
    fake_collection = MagicMock()

    fake_collection.get.return_value = {
        "ids": []
    }

    result = document_exists(
        fake_collection,
        document_id="abc123"
    )

    assert result is False

    fake_collection.get.assert_called_once_with(
        where={"document_id": "abc123"},
        limit=1
    )

def test_add_chunks():
    fake_collection = MagicMock()

    chunks = [
        {
            "document": "physics.pdf",
            "page": 1,
            "chunk_id": 0,
            "text": "Pierwsza zasada termodynamiki."
        }
    ]

    embeddings = np.array([[0.1, 0.2, 0.3]])

    add_chunks(
        fake_collection,
        chunks,
        embeddings,
        document_id="abc123"
    )

    fake_collection.upsert.assert_called_once_with(
        ids=["abc123_0"],
        documents=["Pierwsza zasada termodynamiki."],
        metadatas=[
            {
                "document_id": "abc123",
                "document": "physics.pdf",
                "page": 1,
                "chunk_id": 0
            }
        ],
        embeddings=[[0.1, 0.2, 0.3]]
    )

def test_add_chunks_mismatched_embeddings():
    fake_collection = MagicMock()

    chunks = [
        {"text": "Fragment pierwszy"},
        {"text": "Fragment drugi"}
    ]

    embeddings = np.array([[0.1, 0.2, 0.3]])

    with pytest.raises(ValueError):
        add_chunks(
            fake_collection,
            chunks,
            embeddings,
            document_id="abc123"
        )

    fake_collection.upsert.assert_not_called()

def test_add_empty_chunks():
    fake_collection = MagicMock()

    add_chunks(
        fake_collection,
        chunks=[],
        embeddings=np.empty((0, 3)),
        document_id="abc123"
    )

    fake_collection.upsert.assert_not_called()

def test_delete_document():
    fake_collection = MagicMock()

    fake_collection.get.return_value = {
        "ids": ["abc123_0", "abc123_1"]
    }

    delete_document(fake_collection, document_id="abc123")

    fake_collection.get.assert_called_once_with(
        where={"document_id": "abc123"}
    )

    fake_collection.delete.assert_called_once_with(
        ids=["abc123_0", "abc123_1"]
    )