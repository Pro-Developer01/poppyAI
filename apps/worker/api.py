from fastapi import FastAPI
from pydantic import BaseModel
from .embeddings import embed_query
from .vectorstore import search
from .llm import generate_answer

app = FastAPI()

class QueryIn(BaseModel):
    question: str
    document_id: str | None = None
    top_k: int = 5

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/query")
def query(body: QueryIn):
    qvec = embed_query(body.question)
    hits = search(qvec, body.top_k, body.document_id)

    citations = [
        {
            "text":        h.payload["text"],
            "document_id": h.payload["document_id"],
            "filename":    h.payload.get("filename"),
            "chunk_index": h.payload.get("chunk_index"),
            "score":       h.score,
        }
        for h in hits
    ]
    answer = generate_answer(body.question, citations)
    return {"answer": answer, "citations": citations}