"""
Document ingestion service.

Loads PDFs and Word docs from DOCS_FOLDER_PATH, chunks them,
embeds them, and upserts into ChromaDB.
"""

import logging
import shutil
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document

from config import get_settings
from services.rag import get_vector_store

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 100
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}


def _load_file(path: Path) -> list[Document]:
    """Load a single file and return a list of LangChain Documents."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))
        elif suffix in {".docx", ".doc"}:
            loader = Docx2txtLoader(str(path))
        else:
            return []
        docs = loader.load()
        # Tag each chunk with the source filename
        for doc in docs:
            doc.metadata["source"] = path.name
        return docs
    except Exception:
        logger.exception("Failed to load file: %s", path)
        return []


def ingest_documents() -> dict[str, int]:
    """
    Scan DOCS_FOLDER_PATH, load all supported files, chunk them,
    and upsert into ChromaDB. Returns a summary dict.
    """
    settings = get_settings()
    docs_path = Path(settings.docs_folder_path)

    if not docs_path.exists():
        logger.warning("Docs folder does not exist: %s", docs_path)
        return {"files_found": 0, "chunks_indexed": 0}

    files = [p for p in docs_path.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    logger.info("Found %d document(s) to ingest", len(files))

    raw_docs: list[Document] = []
    for f in files:
        raw_docs.extend(_load_file(f))

    if not raw_docs:
        logger.info("No content extracted from documents.")
        return {"files_found": len(files), "chunks_indexed": 0}

    # Wipe existing ChromaDB to prevent duplicates accumulating across restarts
    chroma_dir = Path(settings.chroma_persist_dir)
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        logger.info("Cleared existing ChromaDB at %s", chroma_dir)
    get_vector_store.cache_clear()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(raw_docs)
    logger.info("Split into %d chunks", len(chunks))

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    logger.info("Indexed %d chunks into ChromaDB", len(chunks))

    return {"files_found": len(files), "chunks_indexed": len(chunks)}
