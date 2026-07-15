# RAG System

This project is a lightweight Retrieval-Augmented Generation (RAG) pipeline for answering questions from company policy data stored in a local Chroma vector database.

## Project Overview

The workspace contains a simple end-to-end RAG workflow:

1. Load policy documents from the `docs/` folder.
2. Split the text into smaller chunks.
3. Generate embeddings and store them in ChromaDB.
4. Retrieve the most relevant chunks for a user question.
5. Generate a grounded answer using the retrieved context.

## Folder Structure

- `ingestion_pipeline.py`  
  Builds the vector store from the policy documents.

- `retrieval_pipeline.py`  
  Retrieves relevant document chunks for a supplied question.

- `answer_generation.py`  
  Retrieves context and generates a final answer.

- `history_aware_generation.py`  
  Supports a simple multi-turn chat-style workflow using conversation history.

- `multi_query_retrieval.py`  
  Generates multiple query variations, retrieves results for each, and produces a final answer.

- `recursive_character_text_spliiter.py`  
  Demonstrates how `CharacterTextSplitter` and `RecursiveCharacterTextSplitter` behave on sample text.

- `docs/policy_data.txt`  
  Source policy dataset used for retrieval.

- `db/chroma_db/`  
  Persisted Chroma vector store created during ingestion.

## Data Description

The source dataset in `docs/policy_data.txt` contains policy records grouped into categories such as:

- Remote Work & Hours
- Health & Wellness
- Office & Security
- Expense & Travel
- Time Off & Leave
- IT & Hardware
- Benefits & Perks
- Performance & Growth

It also includes reference codes such as `OX-1001`, `OX-1002`, and similar policy IDs that are used to trace specific policy statements.

## Environment Setup

The project expects an environment variable named `OPENROUTER_API_KEY`.

You can place it in a `.env` file in the project root or inside the `venv` directory.

Example:

```env
OPENROUTER_API_KEY=your_api_key_here
```

## Running the Pipeline

From the project root, use the project virtual environment Python executable.

### 1. Build or load the vector store

```powershell
Set-Location "c:\Users\my\Desktop\RAG SYSTEM"
& "c:/Users/my/Desktop/RAG SYSTEM/venv/Scripts/python.exe" ingestion_pipeline.py
```

### 2. Run direct retrieval

```powershell
Set-Location "c:\Users\my\Desktop\RAG SYSTEM"
& "c:/Users/my/Desktop/RAG SYSTEM/venv/Scripts/python.exe" retrieval_pipeline.py "What are the core collaboration hours for all teams as defined in reference code"
```

### 3. Generate a grounded answer

```powershell
Set-Location "c:\Users\my\Desktop\RAG SYSTEM"
& "c:/Users/my/Desktop/RAG SYSTEM/venv/Scripts/python.exe" answer_generation.py "What are the core collaboration hours for all teams as defined in reference code"
```

### 4. Use the history-aware chat flow

```powershell
Set-Location "c:\Users\my\Desktop\RAG SYSTEM"
& "c:/Users/my/Desktop/RAG SYSTEM/venv/Scripts/python.exe" history_aware_generation.py "What are the core collaboration hours for all teams as defined in reference code"
```

### 5. Use the multi-query retrieval flow

```powershell
Set-Location "c:\Users\my\Desktop\RAG SYSTEM"
& "c:/Users/my/Desktop/RAG SYSTEM/venv/Scripts/python.exe" multi_query_retrieval.py
```

If a question is not passed as a command-line argument, the script will prompt for one interactively.

## Notes

- The retrieval workflow depends on the persisted Chroma index in `db/chroma_db/`.
- If the database is missing or empty, run `ingestion_pipeline.py` first.
- The source document file contains policy data in a semi-structured layout, so chunking and retrieval may return multiple policy fragments related to the same topic.
