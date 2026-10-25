import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from chunking import split_pages


def test_short_text():
    pages = [
        {
            "page": 1,
            "text": "Pierwsza zasada termodynamiki opisuje zachowanie energii."
        }
    ]

    chunks = split_pages(
        pages,
        filename="test.pdf",
        chunk_size=500,
        overlap=100
    )

    assert len(chunks) == 1
    assert chunks[0]["page"] == 1
    assert chunks[0]["document"] == "test.pdf"
    assert chunks[0]["text"] == pages[0]["text"]

def test_long_text_creates_multiple_chunks():
    pages = [
        {
            "page": 1,
            "text": "Termodynamika opisuje przemiany energii. " * 20
        }
    ]

    chunks = split_pages(
        pages,
        filename="test.pdf",
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk["document"] == "test.pdf"
        assert chunk["page"] == 1
        assert len(chunk["text"]) > 0