# agent/nodes.py
from ..embeddings import embed_query
from ..vectorstore import search
from ..llm import complete, generate_answer
from .state import AgentState

MAX_ATTEMPTS = 2

# ---------- 1. ROUTE ----------
ROUTE_SYSTEM = (
    "Classify the user question into exactly one word:\n"
    "rag    - answerable from the user's uploaded documents (invoices, reports, contracts, data)\n"
    "web    - needs current/external information not in private documents\n"
    "direct - greeting, chit-chat, or about this assistant itself\n"
    "Reply with only the single word."
)

def route(state: AgentState) -> AgentState:
    label = complete(ROUTE_SYSTEM, state["question"]).lower()
    if label not in ("rag", "web", "direct"):
        label = "rag"   # unsure? documents pehle try karo — safe default
    return {"route": label, "query": state["question"], "attempts": 0}

# ---------- 2. RETRIEVE (Chapter 2 reuse) ----------
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

def rewrite(state: AgentState) -> AgentState:
    new_q = complete(REWRITE_SYSTEM,
                     f"Original question: {state['question']}\n"
                     f"Previous query that failed: {state['query']}")
    return {"query": new_q}

# ---------- 5. WEB SEARCH (Phase 2 stub -> Phase 3 mein MCP tool) ----------
def web_search(state: AgentState) -> AgentState:
    # Yahan koi bhi search API laga sakte ho (Tavily / Brave / SerpAPI).
    # Phase 2 mein hum ise saaf-saaf stub rakhte hain; MCP-based tool Phase 3 mein.
    return {"contexts": [{
        "text": "(web search tool not configured yet - Phase 3)",
        "filename": "web", "chunk_index": 0, "document_id": "web", "score": 0.0,
    }]}

# ---------- 6. GENERATE / DIRECT ----------
def generate(state: AgentState) -> AgentState:
    answer = generate_answer(state["question"], state["contexts"])  # Chapter 2 reuse
    return {"answer": answer}

def direct_answer(state: AgentState) -> AgentState:
    answer = complete(
        "You are a helpful document-intelligence assistant. Answer briefly.",
        state["question"], temperature=0.5,
    )
    return {"answer": answer, "contexts": []}