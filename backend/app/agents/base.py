import os
from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.config import settings

# LangSmith env vars are read by langsmith client automatically
if settings.LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT


def get_llm(model: str | None = None, temperature: float = 0.1) -> ChatOllama:
    return ChatOllama(
        model=model or settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
    )


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.OLLAMA_EMBED_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
