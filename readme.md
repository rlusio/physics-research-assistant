# Physics Research Assistant

A simple RAG (Retrieval-Augmented Generation) application for asking questions about scientific PDF documents.

I built this project to learn how to combine LLMs, vector databases and Python APIs. The main goal is to upload physics-related materials and ask questions based on their content.

## Features

- Upload and process PDF documents
- Split extracted text into smaller chunks
- Generate embeddings and store them in ChromaDB
- Search for relevant fragments using semantic similarity
- Generate answers with a local LLM (Llama 3.2)
- Display source documents and page numbers
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
4. When a question is submitted, the application searches for similar chunks.
5. The retrieved fragments are passed to Llama 3.2 as context.
6. The generated answer and retrieved sources are displayed in Streamlit.

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

## Testing

The project includes unit tests for the API, text chunking, vector store operations and RAG pipeline.

Tests are written using `pytest`, with mocks for external components. GitHub Actions is used to run tests automatically.

## Limitations and future improvements

The application is currently intended for local use.

Some possible improvements include better handling of mathematical formulas in PDFs, improving retrieval quality and adding more tests for the complete RAG workflow.