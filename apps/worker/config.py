import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    qdrant_url:   str = os.getenv("QDRANT_URL", "http://localhost:6333")
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/docs")
    llm_api_key:  str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    embed_model:  str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    chat_model:   str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    embed_dim:    int = int(os.getenv("EMBED_DIM", "1536"))

settings = Settings()
