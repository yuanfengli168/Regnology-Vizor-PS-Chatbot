"""
RAG (Retrieval-Augmented Generation) service.

Provides:
- get_vector_store()  — singleton ChromaDB vector store
- answer_with_rag()   — retrieves relevant docs then streams an LLM response
"""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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

TOP_K = 5  # Number of document chunks to retrieve


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
    return Chroma(
        collection_name="vizor_docs",
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        streaming=True,
        temperature=0.2,
    )


def _retrieve_context(query: str) -> str:
    """Retrieve the top-K most relevant chunks from ChromaDB."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=TOP_K)
    if not results:
        return ""
    parts = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[{i}] (Source: {source})\n{doc.page_content}")
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
    # Include recent conversation history
    for msg in history[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=question))

    llm = get_llm()
    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            yield token
