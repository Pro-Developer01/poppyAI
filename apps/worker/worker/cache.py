import hashlib
import uuid
from qdrant_client import models
from .vectorstore import client          # wahi Qdrant client reuse
from .embeddings import embed_query
from .config import settings

CACHE_COLLECTION = "query_cache"
SIM_THRESHOLD = 0.95      # bahut high rakha hai — galat cache hit poison hota hai

_exact: dict[str, dict] = {}              # in-process exact cache

def _norm(q: str) -> str:
    return " ".join(q.lower().split())

def _key(q: str, document_id: str | None) -> str:
    return hashlib.sha256(f"{_norm(q)}|{document_id}".encode()).hexdigest()

def ensure_cache_collection():
    names = [c.name for c in client.get_collections().collections]
    if CACHE_COLLECTION not in names:
        client.create_collection(
            collection_name=CACHE_COLLECTION,
            vectors_config=models.VectorParams(
                size=settings.embed_dim, distance=models.Distance.COSINE),
        )

def get(question: str, document_id: str | None):
    # L1: exact
    hit = _exact.get(_key(question, document_id))
    if hit:
        return {**hit, "cache": "exact"}
    # L2: semantic
    ensure_cache_collection()
    qvec = embed_query(question)           # NOTE: ye 1 embedding call kharch hota hai
    res = client.query_points(
        collection_name=CACHE_COLLECTION, query=qvec, limit=1, with_payload=True)
    if res.points and res.points[0].score >= SIM_THRESHOLD:
        p = res.points[0].payload
        if p.get("document_id") == document_id:      # doc-scope match zaroori
            return {"answer": p["answer"], "citations": p.get("citations", []),
                    "cache": "semantic"}
    return None

def put(question: str, document_id: str | None, answer: str, citations: list):
    entry = {"answer": answer, "citations": citations}
    _exact[_key(question, document_id)] = entry
    qvec = embed_query(question)
    client.upsert(collection_name=CACHE_COLLECTION, points=[
        models.PointStruct(id=str(uuid.uuid4()), vector=qvec, payload={
            "question": question, "document_id": document_id,
            "answer": answer, "citations": citations,
        })
    ])