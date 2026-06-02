from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings

_model = None

def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)

    return _model

def get_embedding_dimension():
    model = get_embedding_model()

    dimension = model.get_sentence_embedding_dimension()

    if dimension is None:
        raise RuntimeError("Could not determine embedding dimension.")

    return int(dimension)

def embed_text(text: str) -> List[float]:
    model = get_embedding_model()

    vector = model.encode(
        text,
        normalize_embeddings=True,
    )

    return vector.tolist()

def embed_texts(texts: List[str]):
    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    )

    return vectors.tolist()