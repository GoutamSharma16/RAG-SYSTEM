# RAG Pipeline — Project README

This project is a small Retrieval-Augmented Generation (RAG) pipeline built with **LangChain**, **ChromaDB**, and **OpenRouter** (used as an OpenAI-compatible API). The core logic lives in `script.py`, a single-file, mode-based CLI. Everything else in this folder is a **thin compatibility wrapper**: a set of legacy, individually-named entrypoints that were kept around (or created) so older commands/scripts still work, while all real logic now lives in one place.

> Note: `README.md` in the uploads was empty — this file replaces it as the project's actual documentation.

## Project structure

```
script.py                              # core pipeline — all real logic lives here
ingestion_pipeline.py                  # wrapper → script.run_ingestion()
retrieval_pipeline.py                  # wrapper → script.run_retrieval()
answer_generation.py                   # wrapper → script.answer_query()
multi_query_retrieval.py               # wrapper → script.run_multi_query_retrieval()
history_aware_generation.py            # wrapper → script.history_aware_answer() / run_history_chat_loop()
recursive_character_text_spliiter.py   # wrapper → script.run_splitter_demo()
run_all_rag.py                         # wrapper → script.run_all_flows() (interactive loop)
docs/                                  # put your .txt source documents here (not included)
db/chroma_db/                          # persisted vector store, created by ingestion
```

## How the wrappers work

Each wrapper follows the same pattern:

1. Import the real function from `script.py`.
2. Read a question from `sys.argv`, filtering out shell/interpreter noise (flags like `-u`, `--`, `cd /d ...`, `python.exe`, the wrapper's own filename, `&&` chains) via a local `looks_like_runner_command()` helper, so a stray launch command never gets treated as the user's actual question.
3. If no valid question was passed as an argument, fall back to an interactive `input("Enter your question: ")` prompt.
4. Call the corresponding `script.py` function and let it print the results.

This means **every wrapper is equivalent to running `script.py` in the matching mode** — they exist purely for convenience/backward compatibility (e.g. if you or a tool is used to invoking `python answer_generation.py "..."` instead of `python script.py answer "..."`).

## Wrapper-to-mode mapping

| Wrapper script | Equivalent `script.py` command | Underlying function |
|---|---|---|
| `ingestion_pipeline.py` | `python script.py ingest` | `run_ingestion()` |
| `retrieval_pipeline.py` | `python script.py retrieve "question"` | `run_retrieval()` |
| `answer_generation.py` | `python script.py answer "question"` | `answer_query()` |
| `multi_query_retrieval.py` | `python script.py multi "question"` | `run_multi_query_retrieval()` |
| `history_aware_generation.py` | `python script.py chat` (or one-shot with a question arg) | `history_aware_answer()` / `run_history_chat_loop()` |
| `recursive_character_text_spliiter.py` | `python script.py splitter` | `run_splitter_demo()` |
| `run_all_rag.py` | `python script.py all "question"` (looped interactively) | `run_all_flows()` |

## Usage

Run `ingestion_pipeline.py` (or `python script.py ingest`) once to build the vector store from `docs/*.txt` files, then use any of the other wrappers to query it:

```bash
python ingestion_pipeline.py
python retrieval_pipeline.py "What is the PTO policy?"
python answer_generation.py "What is the PTO policy?"
python multi_query_retrieval.py "What is the PTO policy?"
python history_aware_generation.py "What is the PTO policy?"
python recursive_character_text_spliiter.py
python run_all_rag.py
```

All wrappers require the same setup as `script.py`: an `OPENROUTER_API_KEY` in a `.env` file, and `docs/` populated with `.txt` files before ingestion.

## Details worth knowing

- **`history_aware_generation.py`** starts a *fresh* `chat_history = []` on every one-shot call (when a question is passed as an argument) — history only accumulates within `run_history_chat_loop()`'s interactive session, not across separate wrapper invocations.
- **`run_all_rag.py`** behaves differently from the others: instead of taking a single question and exiting, it loops indefinitely, running the *entire* `run_all_flows()` sequence (retrieve → answer → multi-query → history-aware) for every question typed, until you type `quit`.
- **`recursive_character_text_spliiter.py`** (note the typo in the filename — "spliiter") just calls `run_splitter_demo()`, which currently produces no visible output since that function never calls its own internal `print_chunks()` helper on any sample text. See `script.py`'s README for the fix.
- Each wrapper duplicates its own copy of `looks_like_runner_command()` / `extract_query_from_args()` rather than importing them from `script.py` — functionally fine, but means any future fix to that filtering logic needs to be applied in every wrapper file individually, plus in `script.py`'s own copy.
- `answer_generation.py`'s argument filter is slightly stricter than the others: it drops any argument starting with `-` outright, in addition to the shared `looks_like_runner_command()` check.
