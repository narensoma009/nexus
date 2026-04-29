import os
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel

from app.config import settings


if settings.LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT


def get_llm(model: str | None = None, temperature: float = 0.1) -> BaseChatModel:
    mode = settings.LLM_MODE.lower()

    if mode == "mock":
        from app.agents.mock_llm import MockChatLLM
        return MockChatLLM()

    if mode == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model or settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
        )

    if mode == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
            temperature=temperature,
        )

    raise ValueError(f"Unknown LLM_MODE: {settings.LLM_MODE}")


def get_embeddings() -> Embeddings:
    mode = settings.LLM_MODE.lower()

    if mode == "mock":
        from app.agents.mock_llm import MockEmbeddings
        return MockEmbeddings()

    if mode == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    if mode == "azure_openai":
        from langchain_openai import AzureOpenAIEmbeddings
        return AzureOpenAIEmbeddings(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_deployment=os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small"),
        )

    raise ValueError(f"Unknown LLM_MODE: {settings.LLM_MODE}")
