import sys
from types import ModuleType
from unittest.mock import MagicMock

# Zastępujemy moduł odpowiedzialny za generowanie odpowiedzi
fake_rag = ModuleType("rag_pipeline")
fake_rag.generate_answer = MagicMock(name="generate_answer")

# Zastępujemy moduł odpowiedzialny za embeddingi
fake_embeddings = ModuleType("embeddings")
fake_embeddings.generate_embeddings = MagicMock(
    name="generate_embeddings"
)

sys.modules["rag_pipeline"] = fake_rag
sys.modules["embeddings"] = fake_embeddings
