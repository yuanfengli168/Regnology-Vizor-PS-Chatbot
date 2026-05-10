"""
RAG (Retrieval-Augmented Generation) service.

Supports two LLM providers, switched via LLM_PROVIDER in .env:
  - "openai"  — OpenAI ChatOpenAI + OpenAIEmbeddings (default)
  - "ollama"  — local Ollama ChatOllama + OllamaEmbeddings (no API key needed)

Provides:
- get_vector_store()  — singleton ChromaDB vector store
- answer_with_rag()   — retrieves relevant docs then streams an LLM response
"""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful internal assistant for the Regnology Vizor Professional Services team.
Your job is to help team members — especially new joiners — understand the Vizor product by answering \
questions based on the provided documentation.

Rules:
- Answer based on the retrieved documentation excerpts provided below.
- If the documentation does not contain enough information to answer, say so clearly. Do not make things up.
- Be concise, accurate, and friendly.
- Use markdown formatting (bullet points, code blocks, tables) when it improves readability.
"""

TOP_K = 10


def _make_embeddings():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        logger.info("Using Ollama embeddings: %s", settings.ollama_embedding_model)
        return OllamaEmbeddings(
            model=settings.ollama_embedding_model,
            base_url=settings.ollama_base_url,
        )
    else:
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using OpenAI embeddings: %s", settings.openai_embedding_model)
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )


def _make_llm():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        logger.info("Using Ollama LLM: %s", settings.ollama_model)
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )
    else:
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenAI LLM: %s", settings.openai_model)
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            streaming=True,
            temperature=0.2,
        )


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    return Chroma(
        collection_name="vizor_docs",
        embedding_function=_make_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


@lru_cache(maxsize=1)
def get_llm():
    return _make_llm()


def _retrieve_context(query: str) -> str:
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(query, k=TOP_K)
    if not results:
        logger.info("RAG retrieval: no chunks found for query: %s", query[:80])
        return ""
    parts = []
    logger.info("RAG retrieval for query: %r", query[:80])
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:120].replace("\n", " ")
        logger.info("  [%d] score=%.4f  src=%s  page=%s  preview: %s", i, score, source, page, preview)
        parts.append(f"[{i}] (Source: {source}, page {page})\n{doc.page_content}")
    return "\n\n".join(parts)


async def answer_with_rag(
    question: str,
    history: list[dict[str, str]],
) -> AsyncIterator[str]:
    """
    Retrieve relevant doc chunks, build a prompt, and stream the LLM response.
    Yields string tokens one at a time.
    """
    context = _retrieve_context(question)

    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\n--- Retrieved Documentation ---\n{context}\n---"

    messages = [SystemMessage(content=system_content)]
    for msg in history[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=question))

    llm = get_llm()
    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            yield token

