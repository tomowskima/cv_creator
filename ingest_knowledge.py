import json
import os
from hashlib import md5
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from openai import OpenAI
from pypdf import PdfReader

from app.config import ModelConfig, get_model_config

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
OUTPUT_PATH = KNOWLEDGE_DIR / "ingested_chunks.json"
STATE_PATH = KNOWLEDGE_DIR / ".ingest_state.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
EMBED_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def _load_state() -> Dict[str, str]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def _save_state(state: Dict[str, str]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def _compute_signature(files: Sequence[Path]) -> str:
    hasher = md5()
    for path in sorted(files):
        stat = path.stat()
        hasher.update(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}".encode("utf-8"))
    return hasher.hexdigest()


def _extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text)
    return "\n".join(pages)


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: List[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(cleaned[start:end])
        if end == length:
            break
        start = max(0, end - overlap)
    return chunks


def _batch(iterable: Sequence[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(iterable), size):
        yield list(iterable[i : i + size])


def _embed_chunks(chunks: List[str], client: OpenAI) -> List[List[float]]:
    if not chunks:
        return []

    embeddings: List[List[float]] = []
    for batch in _batch(chunks, 20):
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])
    return embeddings


def ingest(force: bool = False) -> Path:
    KNOWLEDGE_DIR.mkdir(exist_ok=True)

    kb_files = [p for p in KNOWLEDGE_DIR.glob("*.pdf") if p.is_file()]
    signature = _compute_signature(kb_files)
    state = _load_state()

    if not force and state.get("signature") == signature and OUTPUT_PATH.exists():
        return OUTPUT_PATH

    model_config: ModelConfig = get_model_config()
    if not model_config.is_configured:
        raise RuntimeError(
            "Brak OPENAI_API_KEY – nie można obliczyć embeddingów dla knowledge_base."
        )

    client = OpenAI(api_key=model_config.api_key)
    all_chunks: List[Dict[str, object]] = []

    for pdf_path in kb_files:
        text = _extract_text_from_pdf(pdf_path)
        chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        embeddings = _embed_chunks(chunks, client)
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            all_chunks.append(
                {
                    "source": pdf_path.name,
                    "chunk_id": f"{pdf_path.stem}#{idx}",
                    "content": chunk,
                    "embedding": emb,
                }
            )

    OUTPUT_PATH.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2))
    _save_state({"signature": signature})
    return OUTPUT_PATH


if __name__ == "__main__":
    path = ingest(force=True)
    print(f"Ingestion finished. Data saved to {path}")

