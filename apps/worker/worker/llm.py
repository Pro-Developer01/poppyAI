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


def complete(system: str, user: str, temperature: float = 0.0) -> str:
    resp = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def stream_answer(question: str, contexts: list[dict]):
    blocks = [
        f"[{i}] (from {c.get('filename')}, chunk {c.get('chunk_index')}):\n{c['text']}"
        for i, c in enumerate(contexts, start=1)
    ]
    context_text = "\n\n".join(blocks)
    
    user = (f"Context:\n" + context_text +f"\n\nQuestion: {question}\n\nAnswer with inline [n] citations.")
    stream = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user",   "content": user}],
        temperature=0.1,
        stream=True,                      # <-- token-by-token
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta