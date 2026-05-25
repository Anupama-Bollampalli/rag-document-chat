import os
import uuid
import PyPDF2
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings


CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

_model = None
_client = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.Client(Settings(anonymized_telemetry=False))
        _collection = _client.get_or_create_collection("documents")
    return _collection


def _chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if len(c.strip()) > 30]


def ingest_document(filename: str, content: bytes, is_pdf: bool) -> dict:
    if is_pdf:
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = content.decode("utf-8", errors="ignore")

    chunks = _chunk_text(text)
    model = _get_model()
    embeddings = model.encode(chunks).tolist()

    collection = _get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=[{"source": filename, "chunk_index": i} for i, _ in enumerate(chunks)],
    )
    return {"filename": filename, "chunks": len(chunks), "total_chars": len(text)}


def retrieve(query: str) -> list[dict]:
    model = _get_model()
    query_embedding = model.encode([query]).tolist()[0]
    collection = _get_collection()
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K, count),
    )
    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "source": results["metadatas"][0][i].get("source", "unknown"),
            "score": float(1 - results["distances"][0][i]) if results.get("distances") else 0.9,
        })
    return chunks


def list_documents() -> list[str]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.get()
    sources = list({m["source"] for m in results["metadatas"]})
    return sorted(sources)
