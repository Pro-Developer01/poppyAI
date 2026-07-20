# agent/nodes.py
import json
from ..embeddings import embed_query
from ..vectorstore import search
from ..llm import complete, generate_answer
from .state import AgentState
from langfuse import observe
from ..mcp_client import call_tool

MAX_ATTEMPTS = 2

# ---------- 1. ROUTE ----------
ROUTE_SYSTEM = (
    "Classify the user question into exactly one word:\n"
    "rag    - answerable from the user's uploaded documents (invoices, reports, contracts, data)\n"
    "web    - needs current/external information not in private documents\n"
    "direct - greeting, chit-chat, or about this assistant itself\n"
    "complex - comparison or multi-part question needing multiple lookups\n"
    "Reply with only the single word."
)

@observe
def route(state: AgentState) -> AgentState:
    label = complete(ROUTE_SYSTEM, state["question"]).lower()
    if label not in ("rag", "web", "direct"):
        label = "rag"   # unsure? documents pehle try karo — safe default
    return {"route": label, "query": state["question"], "attempts": 0}

# ---------- 2. RETRIEVE (Chapter 2 reuse) ----------
@observe
def retrieve(state: AgentState) -> AgentState:
    qvec = embed_query(state["query"])
    hits = search(qvec, state.get("top_k", 5), state.get("document_id"))
    contexts = [
        {
            "text":        h.payload["text"],
            "filename":    h.payload.get("filename"),
            "chunk_index": h.payload.get("chunk_index"),
            "document_id": h.payload["document_id"],
            "score":       h.score,
        }
        for h in hits
    ]
    return {"contexts": contexts, "attempts": state.get("attempts", 0) + 1}

# ---------- 3. GRADE ----------
GRADE_SYSTEM = (
    "You are a strict relevance grader. Given a question and retrieved snippets, "
    "answer 'yes' if the snippets contain enough information to answer the question, "
    "otherwise 'no'. Reply with only yes or no."
)
@observe    
def grade(state: AgentState) -> AgentState:
    snippets = "\n---\n".join(c["text"][:500] for c in state["contexts"][:5])
    verdict = complete(GRADE_SYSTEM,
                       f"Question: {state['question']}\n\nSnippets:\n{snippets}")
    return {"relevant": verdict.lower().startswith("y")}

# ---------- 4. REWRITE ----------
REWRITE_SYSTEM = (
    "Rewrite the search query to better match how the information would be phrased "
    "inside business documents. Keep it short. Reply with only the rewritten query."
)

@observe
def rewrite(state: AgentState) -> AgentState:
    new_q = complete(REWRITE_SYSTEM,
                     f"Original question: {state['question']}\n"
                     f"Previous query that failed: {state['query']}")
    return {"query": new_q}

# ---------- 5. WEB SEARCH (Phase 2 stub -> Phase 3 mein MCP tool) ----------
@observe    
def web_search(state: AgentState) -> AgentState:
    # Yahan koi bhi search API laga sakte ho (Tavily / Brave / SerpAPI).
    # Phase 2 mein hum ise saaf-saaf stub rakhte hain; MCP-based tool Phase 3 mein.
    return {"contexts": [{
        "text": "(web search tool not configured yet - Phase 3)",
        "filename": "web", "chunk_index": 0, "document_id": "web", "score": 0.0,
    }]}

# ---------- 6. GENERATE / DIRECT ----------
@observe
def generate(state: AgentState) -> AgentState:
    answer = generate_answer(state["question"], state["contexts"])  # Chapter 2 reuse
    return {"answer": answer}

@observe
def direct_answer(state: AgentState) -> AgentState:
    answer = complete(
        "You are a helpful document-intelligence assistant. Answer briefly.",
        state["question"], temperature=0.5,
    )
    return {"answer": answer, "contexts": []}


@observe()
def web_search(state: AgentState) -> AgentState:
    raw = call_tool("web_search", {"query": state["query"], "max_results": 3})
    results = json.loads(raw)
    contexts = [
        {
            "text":        r["content"],
            "filename":    r["url"],          # citation = URL
            "chunk_index": i,
            "document_id": "web",
            "score":       0.0,
        }
        for i, r in enumerate(results)
    ]
    return {"contexts": contexts}

# ---------- 7. PLAN ----------
PLAN_SYSTEM = (
    "Decide if the question needs to be broken into sub-questions "
    "(e.g. comparisons, multi-part questions). If it is simple, return a JSON "
    'array with the question as-is: ["<question>"]. If complex, return 2-4 '
    "self-contained sub-questions as a JSON array. Return ONLY the JSON array."
)

@observe()
def plan(state: AgentState) -> AgentState:
    raw = complete(PLAN_SYSTEM, state["question"])
    try:
        subs = json.loads(raw)
        assert isinstance(subs, list) and all(isinstance(s, str) for s in subs)
    except Exception:
        subs = [state["question"]]        # parse fail -> single-shot fallback
    return {"sub_questions": subs[:4], "sub_results": []}

# ---------- 8. EXECUTE (ek sub-question per pass — loop graph karega) ----------
@observe()
def execute_sub(state: AgentState) -> AgentState:
    done = len(state["sub_results"])
    sub_q = state["sub_questions"][done]
    qvec = embed_query(sub_q)
    hits = search(qvec, state.get("top_k", 5), state.get("document_id"))
    contexts = [
        {"text": h.payload["text"], "filename": h.payload.get("filename"),
         "chunk_index": h.payload.get("chunk_index"),
         "document_id": h.payload["document_id"], "score": h.score}
        for h in hits
    ]
    return {"sub_results": state["sub_results"] + [{"question": sub_q,
                                                    "contexts": contexts}]}

# ---------- 9. COMBINE ----------
@observe()
def combine(state: AgentState) -> AgentState:
    all_contexts = []
    for r in state["sub_results"]:
        all_contexts.extend(r["contexts"])
    # dedupe (same chunk do sub-questions se aa sakta hai)
    seen, unique = set(), []
    for c in all_contexts:
        key = (c["document_id"], c["chunk_index"])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    answer = generate_answer(state["question"], unique[:10])
    return {"answer": answer, "contexts": unique[:10]}