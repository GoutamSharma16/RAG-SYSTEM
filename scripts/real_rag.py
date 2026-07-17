from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from typing import Iterable, List, Tuple

# Fix system path paths so it reads from Utils directory flawlessly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "Utils"))

import script
from langchain_chroma import Chroma
from langchain_core.documents import Document

def run_ingestion() -> None:
    print("[ingestion] Delegating pipeline process to script.py functionality...")
    script.run_ingestion()


def run_retrieval(query: str) -> str:
    """Run retrieval and format output contexts cleanly."""
    try:
        docs = script.run_retrieval(query)
        return "Retrieval complete. Results displayed above."
    except Exception as e:
        return f"Error executing retrieval flow: {str(e)}"


def run_all_flows(question: str) -> str:
    """Consolidated entrypoint matching answer_generation configuration blueprints."""
    return script.answer_query(question)