from openai import OpenAI
from .config import settings

_client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

SYSTEM = (
    "You are a document assistant. Answer ONLY from the provided context. "
    "Cite sources inline as [n] using the given source numbers. "
    "If the answer is not in the context, say you don't have enough information."
)

def generate_answer(question: str, contexts: list[dict]) -> str:
    blocks = [
        f"[{i}] (from {c.get('filename')}, chunk {c.get('chunk_index')}):\n{c['text']}"
        for i, c in enumerate(contexts, start=1)
    ]
    context_text = "\n\n".join(blocks)
    user = (
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        f"Answer with inline [n] citations."
    )
    resp = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": user},
        ],
        temperature=0.1,   # factual Q&A ke liye low temperature
    )
    return resp.choices[0].message.content
