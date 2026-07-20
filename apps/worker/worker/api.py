from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from .agent.graph import agent
from . import cache

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
    cached = cache.get(body.question, body.document_id)
    if cached:
        return cached

    result = agent.invoke({
        "question": body.question,
        "document_id": body.document_id,
        "top_k": body.top_k,
    })
    out = {"answer": result["answer"],
           "citations": result.get("contexts", []),
           "route": result.get("route")}
    cache.put(body.question, body.document_id, out["answer"], out["citations"])
    return out




@app.post("/query/stream")
def query_stream(body: QueryIn):
    def event_gen():
        def sse(event: str, data) -> str:
            return f"event: {event}\ndata: {json.dumps(data)}\n\n"

        cached = cache.get(body.question, body.document_id)
        if cached:
            yield sse("stage", {"node": "cache_hit"})
            yield sse("citations", cached["citations"])
            yield sse("token", {"t": cached["answer"]})
            yield sse("done", {})
            return

        state = {"question": body.question,
                 "document_id": body.document_id, "top_k": body.top_k}

        final_state = {}
        # LangGraph stream: har node complete hone pe {node_name: delta} milta hai
        for update in agent.stream(state, stream_mode="updates"):
            for node_name, delta in update.items():
                final_state.update(delta)
                if node_name == "generate":
                    continue   # generate ko hum neeche khud token-stream karenge
                yield sse("stage", {"node": node_name})

        contexts = final_state.get("contexts", [])
        yield sse("citations", contexts)

        # NOTE: simplicity ke liye generate yahan dobara chalta hai (agent ne bhi
        # generate node chalaya tha). Clean fix: graph END ko generate se pehle
        # rakho aur generation hamesha bahar karo — reader exercise / refactor.
        from .llm import stream_answer
        parts = []
        for token in stream_answer(body.question, contexts):
            parts.append(token)
            yield sse("token", {"t": token})

        cache.put(body.question, body.document_id, "".join(parts), contexts)
        yield sse("done", {})

    return StreamingResponse(event_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})