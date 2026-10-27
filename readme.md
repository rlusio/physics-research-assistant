## Demo

![Physics Research Assistant](screenshots/app_ss.png)

# Physics Research Assistant

A simple RAG (Retrieval-Augmented Generation) application for asking questions about scientific PDF documents.

I built this project to learn how to combine LLMs, vector databases and Python APIs. The main goal is to upload physics-related materials and ask questions based on their content.

## Features

- Upload and process PDF documents
- Split extracted text into smaller chunks
- Generate embeddings and store them in ChromaDB
- Search for relevant fragments using semantic similarity and keyword matching
- Generate answers with a local LLM (Llama 3.2)
- Display retrieved source fragments, document names and page numbers
- Avoid indexing the same PDF multiple times

## Technologies

- **Python** – backend logic
- **FastAPI** – REST API
- **Streamlit** – user interface
- **Ollama / Llama 3.2** – local language model
- **ChromaDB** – vector database
- **Sentence Transformers** – text embeddings
- **PyMuPDF** – PDF text extraction
- **Docker Compose** – running the services
- **Pytest and GitHub Actions** – testing and CI

## How it works

1. The user uploads a PDF document.
2. The application extracts text and splits it into chunks.
3. Each chunk is converted into an embedding and stored in ChromaDB.
4. When a question is submitted, the application searches for relevant chunks using semantic similarity and keyword matching.
5. The results are combined, duplicates are removed and the selected fragments are passed to Llama 3.2 as context.
6. The generated answer and retrieved sources are displayed in Streamlit.

The retrieval process uses a simple hybrid approach. Semantic search finds fragments with similar meaning, while keyword matching helps identify specific terms and scientific names.

## Running the project

Docker and Docker Compose are required.

Clone the repository:

```bash
git clone https://github.com/rlusio/physics-research-assistant.git
cd physics-research-assistant
```

Build and start the containers:

```bash
docker compose up -d --build
```

Download the language model into the Ollama container:

```bash
docker compose exec ollama ollama pull llama3.2
```

Open the application:

- Streamlit: http://localhost:8501
- FastAPI documentation: http://localhost:8000/docs

The first startup may take some time because the embedding model needs to be downloaded.

For later startups, run:

```bash
docker compose up -d
```

## Testing

The project includes 28 automated tests covering the API, text chunking, vector store operations, retrieval logic and RAG pipeline.

Tests use `pytest` and mocks for external components, so they do not require running the language model.

Run the tests with:

```bash
docker compose exec backend python -m pytest -v tests/
```

GitHub Actions is configured to run tests automatically.

## Limitations and future improvements

This project is an MVP intended for local use and learning purposes.

- The retrieval system uses simple keyword matching and may not always select the most relevant fragments.
- Keyword search currently scans the stored chunks, so it is not optimized for large document collections.
- Mathematical formulas and complex PDF layouts may not be extracted correctly.
- LLM-generated answers may contain errors or unsupported information, so the original sources should be checked.

Possible future improvements include BM25-based retrieval, reranking, better handling of mathematical formulas and evaluating different language models.
