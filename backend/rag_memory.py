"""
rag_memory.py — Local RAG pipeline using ChromaDB.

Responsibilities:
  • Initialise (or open) a persistent ChromaDB collection per research session.
  • Split incoming text into overlapping chunks via langchain-text-splitters.
  • Embed and store chunks with metadata (source URL, chunk index).
  • Retrieve the top-K most semantically relevant chunks for a query.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Callable

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter

log = logging.getLogger(__name__)


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    text: str
    source_url: str
    chunk_index: int
    doc_id: str


@dataclass
class RetrievedChunk:
    text: str
    source_url: str
    distance: float


# ── Manager ───────────────────────────────────────────────────────────────────

class RAGMemory:
    """
    Wraps a single ChromaDB collection for one research session.

    Parameters
    ----------
    persist_dir : str
        Filesystem path where ChromaDB stores its data.
    session_id : str
        Unique identifier for this research run; used as the collection name.
    chunk_size : int
        Maximum characters per chunk.
    chunk_overlap : int
        Character overlap between adjacent chunks.
    on_log : Callable[[str], None] | None
        Optional callback for status messages (forwarded to GUI log).
    """

    def __init__(
        self,
        persist_dir: str,
        session_id: str,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        on_log: Callable[[str], None] | None = None,
    ) -> None:
        self._log_cb = on_log or (lambda msg: None)
        self.session_id = session_id

        # Sanitise collection name — Chroma requires [a-zA-Z0-9_-] and 3-63 chars
        safe_id = "dr_" + session_id[:40].replace(" ", "_")

        self._log(f"[CHROMA] Opening collection '{safe_id}' at {persist_dir}")
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get-or-create so re-runs don't duplicate
        self._col = self._client.get_or_create_collection(
            name=safe_id,
            metadata={"hnsw:space": "cosine"},
        )

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        self._stored_doc_ids: set[str] = set()
        self.total_chunks: int = 0

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        log.debug(msg)
        self._log_cb(msg)

    @staticmethod
    def _url_hash(url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    # ── Public API ────────────────────────────────────────────────────────────

    def ingest(self, text: str, source_url: str) -> int:
        """
        Chunk *text*, embed, and store in ChromaDB.

        Returns the number of new chunks stored (0 if already ingested).
        """
        doc_id = self._url_hash(source_url)
        if doc_id in self._stored_doc_ids:
            self._log(f"[CHROMA] Already ingested: {source_url[:80]}")
            return 0

        chunks = self._splitter.split_text(text)
        if not chunks:
            self._log(f"[CHROMA] No text extracted from: {source_url[:80]}")
            return 0

        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metas = [{"source_url": source_url, "chunk_index": i} for i in range(len(chunks))]

        # ChromaDB will use its default embedding function (all-MiniLM-L6-v2)
        self._col.add(documents=chunks, metadatas=metas, ids=ids)

        self._stored_doc_ids.add(doc_id)
        self.total_chunks += len(chunks)
        self._log(f"[CHUNKING INTO CHROMA] {len(chunks)} chunks ← {source_url[:70]}")
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 12) -> list[RetrievedChunk]:
        """
        Semantic search: return the top_k most relevant chunks for *query*.
        """
        n_results = min(top_k, self._col.count())
        if n_results == 0:
            return []

        result = self._col.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        chunks: list[RetrievedChunk] = []
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        dists = result["distances"][0]

        for doc, meta, dist in zip(docs, metas, dists):
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    source_url=meta.get("source_url", "unknown"),
                    distance=dist,
                )
            )

        self._log(f"[RETRIEVING] {len(chunks)} chunks for query: '{query[:60]}'")
        return chunks

    def count(self) -> int:
        """Total chunks currently in the collection."""
        return self._col.count()

    def delete_collection(self) -> bool:
        """Drop this session's collection from ChromaDB (cleanup). Returns True if successful."""
        safe_id = "dr_" + self.session_id[:40].replace(" ", "_")
        try:
            # Verify collection exists before deletion
            collections_before = [c.name for c in self._client.list_collections()]
            if safe_id not in collections_before:
                self._log(f"[CHROMA] Collection {safe_id} not found (already deleted or never created)")
                return True
            
            self._client.delete_collection(safe_id)
            
            # Verify deletion
            collections_after = [c.name for c in self._client.list_collections()]
            if safe_id in collections_after:
                self._log(f"[CHROMA] WARNING: Collection {safe_id} still exists after deletion attempt")
                return False
            
            self._log(f"[CHROMA] Collection {safe_id} successfully deleted and verified.")
            return True
        except Exception as exc:
            self._log(f"[CHROMA] Could not delete collection {safe_id}: {exc}")
            return False
