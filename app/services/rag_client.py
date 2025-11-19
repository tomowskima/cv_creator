import json
import math
from pathlib import Path
from typing import List, Tuple

from openai import OpenAI

from ingest_knowledge import EMBED_MODEL, OUTPUT_PATH, ingest

from ..config import ModelConfig, get_model_config

_model_config: ModelConfig = get_model_config()
_client = OpenAI(api_key=_model_config.api_key) if _model_config.is_configured else None

_ingested_path = ingest()
if Path(_ingested_path).exists():
    _CHUNKS = json.loads(Path(_ingested_path).read_text())
else:
    _CHUNKS = []

_EMBEDDINGS: List[List[float]] = [chunk["embedding"] for chunk in _CHUNKS]
_EMBED_NORMS: List[float] = [
    math.sqrt(sum(value * value for value in embedding)) or 1.0
    for embedding in _EMBEDDINGS
]


def _cosine_similarity(
    emb: List[float], emb_norm: float, query_vec: List[float], query_norm: float
) -> float:
    if not emb or not query_vec or emb_norm == 0 or query_norm == 0:
        return 0.0
    dot = sum(a * b for a, b in zip(emb, query_vec))
    return dot / (emb_norm * query_norm)


def _embed_query(query: str) -> Tuple[List[float], float]:
    if not _client:
        return [], 0.0
    response = _client.embeddings.create(model=EMBED_MODEL, input=[query])
    vector = response.data[0].embedding
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return vector, norm


def get_rag_context_for_cv(query: str, limit: int = 3) -> List[str]:
    """
    Zwraca listę fragmentów wiedzy najlepiej dopasowanych do zapytania.
    """

    if not query or not _CHUNKS or not _client:
        return []

    query_vec, query_norm = _embed_query(query)
    if not query_vec:
        return []

    scored = []
    for chunk, emb, emb_norm in zip(_CHUNKS, _EMBEDDINGS, _EMBED_NORMS):
        score = _cosine_similarity(emb, emb_norm, query_vec, query_norm)
        scored.append((score, chunk["content"]))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [content for score, content in scored[:limit] if score > 0]

