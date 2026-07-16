from openai import OpenAI
from .config import settings

_client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

def embed_texts(texts: list[str]) -> list[list[float]]:
    # batch mein bhejo — har chunk ke liye alag call mehnga aur slow hai
    resp = _client.embeddings.create(model=settings.embed_model, input=texts)
    return [d.embedding for d in resp.data]

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]