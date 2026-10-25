
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from rag_pipeline import (
    build_context,
    build_user_prompt,
    build_messages,
    generate_answer
)


def sample_matches():
    return [
        {
            "document": "physics.pdf",
            "page": 3,
            "text": "Energia jest zachowana.",
            "distance": 0.12
        },
        {
            "document": "thermodynamics.pdf",
            "page": 7,
            "text": "Cieplo i praca zmieniaja energie ukladu.",
            "distance": 0.25
        }
    ]


def test_build_context():
    context = build_context(sample_matches())

    assert "[Źródło 1: physics.pdf, strona 3]" in context
    assert "Energia jest zachowana." in context
    assert "[Źródło 2: thermodynamics.pdf, strona 7]" in context
    assert "Cieplo i praca zmieniaja energie ukladu." in context


def test_build_user_prompt():
    context = "Energia jest zachowana."
    question = "Co to jest energia?"

    prompt = build_user_prompt(question, context)

    assert "MATERIAŁY ŹRÓDŁOWE:" in prompt
    assert context in prompt
    assert "PYTANIE:" in prompt
    assert question in prompt


def test_build_messages():
    messages = build_messages(
        "Co to jest energia?",
        sample_matches()
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Energia jest zachowana." in messages[1]["content"]


def test_generate_answer_no_matches():
    with patch("rag_pipeline.search_database", return_value=[]):
        result = generate_answer("Co to jest energia?")

    assert result == {
        "answer": "Nie znaleziono fragmentów w dokumentach.",
        "sources": []
    }


def test_generate_answer_success():
    matches = sample_matches()

    with (
        patch("rag_pipeline.search_database", return_value=matches) as mock_search,
        patch("rag_pipeline.Client") as mock_client
    ):
        mock_client.return_value.chat.return_value = {
            "message": {
                "content": "Energia jest zachowana. [Źródło 1]"
            }
        }

        result = generate_answer("Co to jest energia?")

    assert result["answer"] == "Energia jest zachowana. [Źródło 1]"
    assert len(result["sources"]) == 2
    assert result["sources"][0] == matches[0]
    assert result["sources"][1] == matches[1]

    mock_search.assert_called_once_with(
        "Co to jest energia?",
        top_k=3
    )
    mock_client.return_value.chat.assert_called_once()
