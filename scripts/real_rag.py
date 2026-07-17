"""Minimal runnable RAG stubs.

This repository currently contains wrapper entrypoints, but the concrete
RAG implementation functions (`run_ingestion`, `run_retrieval`,
`run_all_flows`, etc.) are missing.

To make the app runnable end-to-end, this module provides no-op (but safe)
implementations that keep the CLI working.

If you later add a real ingestion/retrieval implementation, replace the
functions here.
"""

from __future__ import annotations


def run_ingestion() -> None:
    # Placeholder: in a full implementation you would build or refresh the
    # vector store here.
    print("[ingestion] Skipped (no ingestion implementation present).")


def run_retrieval(query: str) -> str:
    # Placeholder: in a full implementation you would retrieve from Chroma and
    # generate a grounded answer.
    print(f"[retrieval] Query: {query}")
    return "(stub answer)"


def run_all_flows(question: str) -> str:
    run_ingestion()
    return run_retrieval(question)

