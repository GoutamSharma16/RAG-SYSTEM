# script.py

A single-file, CLI-driven Retrieval-Augmented Generation (RAG) pipeline built with **LangChain**, **ChromaDB**, and **OpenRouter** (as an OpenAI-compatible endpoint). It supports ingesting `.txt` documents into a local vector store, then querying them with several retrieval strategies — plain retrieval, single-shot answer generation, multi-query retrieval, and history-aware chat.

## How it works

1. **Ingest** — loads all `.txt` files from `docs/`, splits them into ~800-character chunks, embeds them with `text-embedding-3-small`, and persists them to a local ChromaDB store at `db/chroma_db`.
2. **Query** — embeds the user's question, retrieves the top-k most similar chunks (cosine similarity), and optionally sends them to `gpt-4o-mini` as grounding context to produce a final answer.

Both the embedding model and chat model are routed through **OpenRouter** rather than OpenAI directly.

## Requirements

```bash
pip install python-dotenv langchain-community langchain-chroma langchain-core langchain-openai langchain-text-splitters
```

## Setup

1. Create a `.env` file in the project root (or `venv/.env`) containing:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```
2. Create a `docs/` folder next to `script.py` and put your `.txt` source documents in it.

## Usage

```bash
python script.py ingest                    # build the vector store from docs/
python script.py retrieve "your question"  # show raw retrieved chunks, no LLM call
python script.py answer "your question"    # retrieve + generate a grounded answer
python script.py multi "your question"     # generate query variations, retrieve for each, dedupe, answer
python script.py chat                      # interactive, history-aware Q&A loop (type 'quit' to exit)
python script.py splitter                  # demo of CharacterTextSplitter vs RecursiveCharacterTextSplitter
python script.py all "your question"       # runs retrieve, answer, multi, and history-aware in sequence
```

You must run `ingest` at least once before any query mode — the other modes raise a `FileNotFoundError`/`RuntimeError` if `db/chroma_db` doesn't exist or is empty.

## Mode reference

| Mode | Function | What it does |
|---|---|---|
| `ingest` | `run_ingestion()` | Loads, chunks, embeds, and persists documents to Chroma |
| `retrieve` | `run_retrieval()` | Prints the top-5 retrieved chunks for a query (no generation) |
| `answer` | `answer_query()` | Retrieves top-5 chunks, builds a grounded prompt, calls the LLM once |
| `multi` | `run_multi_query_retrieval()` | Asks the LLM for 3 alternate phrasings of the query, retrieves for each, merges/dedupes results, then answers |
| `chat` | `run_history_chat_loop()` | Loops on stdin; each turn rewrites the question using prior chat history before retrieving, so follow-ups work |
| `splitter` | `run_splitter_demo()` | Illustrates chunking behavior — **note:** currently builds the splitters but never calls `print_chunks()`, so it produces no output (see Known issues) |
| `all` | `run_all_flows()` | Runs retrieve → answer → multi → history-aware back to back for one question |

## Key components

- **`get_embedding_model()` / `get_chat_model()`** — construct the OpenRouter-backed embedding (`text-embedding-3-small`) and chat (`gpt-4o-mini`, temperature 0) clients.
- **`get_vector_store()`** — opens the persisted Chroma DB, raising clear errors if it's missing or empty.
- **`build_answer_prompt()`** — shared helper that formats retrieved chunks into the grounding prompt used by every answer-generating mode.
- **`looks_like_runner_command()`** — a guard that filters out stray shell/debugger arguments (e.g. `cd /d`, `python.exe`, `run_all_rag.py`) so they aren't mistaken for a real question when reading `sys.argv`.

## Known issues / things to note

- **`splitter` mode currently does nothing visible.** `run_splitter_demo()` defines `character_splitter` and `recursive_splitter` and a nested `print_chunks()` helper, but never actually calls `print_chunks()` on any text — so `python script.py splitter` will run without printing any chunk output. To fix, add a sample `text` string and calls like `print_chunks("Character Splitter", character_splitter, text)`.
- **`chunk_overlap=0`** in the demo splitters means chunks won't share any boundary context — fine for illustrating the difference between splitters, but not representative of typical production settings.
- Ingestion uses **`chunk_size=800, chunk_overlap=0`** — no overlap between chunks may hurt retrieval quality for content that splits mid-thought; consider adding overlap (e.g. 100–150 chars) if answers seem to miss context at chunk boundaries.
- The DirectoryLoader only picks up **`*.txt`** files — other formats in `docs/` (PDF, docx, etc.) are silently ignored.
- No `requirements.txt` is included — see the Requirements section above for the packages to install manually.