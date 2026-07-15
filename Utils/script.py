import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent

for env_file in (BASE_DIR / ".env", BASE_DIR / "venv" / ".env"):
    load_dotenv(str(env_file))



def get_openrouter_api_key():
    """Return the configured OpenRouter API key or raise a clear error."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY is missing. Add it to a .env file in the project root "
            "or export it in your shell before running the pipeline."
        )
    return api_key


def get_embedding_model():
    return OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=get_openrouter_api_key(),
        openai_api_base="https://openrouter.ai/api/v1",
    )


def get_chat_model():
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=get_openrouter_api_key(),
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        max_tokens=500,
    )


def get_vector_store():
    """Open the persisted ChromaDB vector store if it exists and contains documents."""
    persistent_directory = str(BASE_DIR / "db" / "chroma_db")

    if not os.path.exists(persistent_directory):
        raise FileNotFoundError(
            f"Vector store directory not found: {persistent_directory}. Run the ingest mode first."
        )

    db = Chroma(
        persist_directory=persistent_directory,
        embedding_function=get_embedding_model(),
        collection_metadata={"hnsw:space": "cosine"},
    )

    if db._collection.count() == 0:
        raise RuntimeError(
            "❌ No documents found in the vector store. Run the ingest mode first to build the DB."
        )

    return db


def run_splitter_demo():
    """Show how CharacterTextSplitter and RecursiveCharacterTextSplitter behave."""
    def print_chunks(label, splitter, text):
        print("\n" + "=" * 60)
        print(label)
        print("=" * 60)

        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks, 1):
            print(f"Chunk {i}: ({len(chunk)} chars)")
            print(f'"{chunk}"')
            print()

    chunk_size = 100
    chunk_overlap = 0

    character_splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def run_ingestion():
    """Load docs, split them, generate embeddings, and persist the Chroma vector store."""
    docs_path = BASE_DIR / "docs"
    persistent_directory = BASE_DIR / "db" / "chroma_db"

    if not docs_path.exists():
        raise FileNotFoundError(f"The documents directory does not exist: {docs_path}")

    loader = DirectoryLoader(path=str(docs_path), glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        raise FileNotFoundError(f"No text documents were found in {docs_path}")

    print(f"Loaded {len(documents)} document(s) from {docs_path}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=0)
    chunks = splitter.split_documents(documents)

    print(f"Split into {len(chunks)} chunks")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        persist_directory=str(persistent_directory),
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"✅ Ingestion complete. Vector store saved to {persistent_directory}")
    return vectorstore


def get_relevant_docs(db, query, k=5):
    """Retrieve the highest-ranked document chunks for a query."""
    retriever = db.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)

    if not docs:
        raise RuntimeError("❌ No relevant documents were retrieved for the query.")

    return docs


def run_retrieval(query):
    """Retrieve and print context for the supplied question."""
    db = get_vector_store()
    docs = get_relevant_docs(db, query, k=5)

    print(f"User Query: {query}")
    print("--- Context ---")
    for i, doc in enumerate(docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")

    return docs


def build_answer_prompt(query, relevant_docs):
    """Build a grounded answer prompt using the retrieved context."""
    context = "\n\n".join(f"- {doc.page_content}" for doc in relevant_docs)
    return f"""Based on the following documents, please answer this question: {query}

Documents:
{context}

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
"""


def answer_query(query):
    """Run the answer-generation flow for a single question."""
    db = get_vector_store()
    relevant_docs = get_relevant_docs(db, query, k=5)

    print(f"User Query: {query}")
    print("--- Context ---")
    for i, doc in enumerate(relevant_docs, 1):
        print(f"Document {i}:\n{doc.page_content}\n")

    combined_input = build_answer_prompt(query, relevant_docs)
    model = get_chat_model()

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=combined_input),
    ]

    result = model.invoke(messages)

    print("\n--- Generated Response ---")
    print(result.content)
    return result.content


def generate_query_variations(model, original_query):
    """Generate 3 alternative search phrasings for the original question."""
    prompt = f"""Generate exactly 3 short alternative search queries for the following question.
Return only 3 lines, one query per line, with no numbering and no explanation.

Original question: {original_query}
"""

    response = model.invoke(prompt)
    lines = []

    for line in response.content.splitlines():
        cleaned = line.strip().strip("-\"'")
        if cleaned:
            lines.append(cleaned)

    if len(lines) < 3:
        return [
            original_query,
            f"{original_query} reference code",
            f"{original_query} policy document",
        ]

    return lines[:3]


def run_multi_query_retrieval(original_query):
    """Generate multiple search variations, retrieve docs for each, and produce a final answer."""
    db = get_vector_store()
    llm = get_chat_model()
    query_variations = generate_query_variations(llm, original_query)

    print(f"Original Query: {original_query}\n")
    print("Generated Query Variations:")
    for i, variation in enumerate(query_variations, 1):
        print(f"{i}. {variation}")

    print("\n" + "=" * 60)

    retriever = db.as_retriever(search_kwargs={"k": 5})
    all_results = []
    seen_contents = set()

    for i, query in enumerate(query_variations, 1):
        print(f"\n=== RESULTS FOR QUERY {i}: {query} ===")

        docs = retriever.invoke(query)
        print(f"Retrieved {len(docs)} documents:\n")

        for j, doc in enumerate(docs, 1):
            text = doc.page_content.strip()
            if text not in seen_contents:
                seen_contents.add(text)
                all_results.append(doc)

            preview = text[:150].replace("\n", " ")
            print(f"Document {j}:")
            print(f"{preview}...\n")

        print("-" * 50)

    print("\n" + "=" * 60)
    print(f"Multi-Query Retrieval Complete! Unique documents retrieved: {len(all_results)}")

    answer_prompt = build_answer_prompt(original_query, all_results)
    answer_result = llm.invoke(answer_prompt)

    print("\n--- Final Answer ---")
    print(answer_result.content)
    return answer_result.content


def history_aware_answer(user_question, db, model, chat_history):
    """Use retrieval plus chat history to answer a question."""
    print(f"\n--- You asked: {user_question} ---")

    if chat_history:
        rewrite_messages = [
            SystemMessage(
                content="Given the chat history, rewrite the new question to be standalone and searchable. Just return the rewritten question."
            ),
        ] + chat_history + [
            HumanMessage(content=f"New question: {user_question}")
        ]

        rewrite_result = model.invoke(rewrite_messages)
        search_question = rewrite_result.content.strip()
        print(f"Searching for: {search_question}")
    else:
        search_question = user_question

    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(search_question)

    if not docs:
        print("❌ No relevant documents were retrieved for the query.")
        return "I don't have enough information to answer that question based on the provided documents."

    print(f"Found {len(docs)} relevant documents:")
    for i, doc in enumerate(docs, 1):
        preview = "\n".join(doc.page_content.split("\n")[:2])
        print(f"  Doc {i}: {preview}...")

    combined_input = f"""Based on the following documents, please answer this question: {user_question}

    Documents:
    {"\n".join([f"- {doc.page_content}" for doc in docs])}

    Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
    """

    messages = [
        SystemMessage(
            content="You are a helpful assistant that answers questions based on provided documents and conversation history."
        ),
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]

    result = model.invoke(messages)
    answer = result.content

    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))

    print(f"Answer: {answer}")
    return answer


def run_history_chat_loop():
    """Start an interactive history-aware chat loop using the vector store."""
    db = get_vector_store()
    model = get_chat_model()
    chat_history = []

    print("Ask me questions! Type 'quit' to exit.")

    while True:
        question = input("\nYour question: ")

        if question.lower() == 'quit':
            print("Goodbye!")
            break

        history_aware_answer(question, db, model, chat_history)


def looks_like_runner_command(value):
    """Detect debugger or shell launcher noise so it is not treated as a user question."""
    if not value:
        return True

    lower = value.lower().strip()
    return (
        lower in {"--", "-u", "python", "python.exe"}
        or "cd /d" in lower
        or "&&" in lower
        or "run_all_rag.py" in lower
        or "script.py" in lower
        or "python.exe" in lower
        or "venv\\scripts\\python.exe" in lower
        or ("python" in lower and (".py" in lower or "python.exe" in lower or "scripts" in lower))
    )


def prompt_question():
    """Read a question from the CLI or from an interactive prompt."""
    if len(sys.argv) > 2:
        joined_args = " ".join(sys.argv[2:]).strip()
        if joined_args and not looks_like_runner_command(joined_args):
            return joined_args

    return input("Enter your question: ").strip()


def run_all_flows(query):
    """Run the retrieval, answer, multi-query, and history-aware flows for one question."""
    print("\n" + "=" * 70)
    print("RUNNING: Retrieval Pipeline")
    print("=" * 70)
    run_retrieval(query)

    print("\n" + "=" * 70)
    print("RUNNING: Answer Generation")
    print("=" * 70)
    answer_query(query)

    print("\n" + "=" * 70)
    print("RUNNING: Multi-Query Retrieval")
    print("=" * 70)
    run_multi_query_retrieval(query)

    print("\n" + "=" * 70)
    print("RUNNING: History-Aware Generation")
    print("=" * 70)
    db = get_vector_store()
    model = get_chat_model()
    chat_history = []
    history_aware_answer(query, db, model, chat_history)


def main():
    """Single-file launcher with the full RAG workflow modes."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python script.py ingest")
        print("  python script.py retrieve \"your question\"")
        print("  python script.py answer \"your question\"")
        print("  python script.py multi \"your question\"")
        print("  python script.py chat")
        print("  python script.py splitter")
        print("  python script.py all \"your question\"")
        return

    mode = sys.argv[1].lower()

    if mode == "ingest":
        run_ingestion()
        return

    if mode == "retrieve":
        query = prompt_question()
        if not query:
            print("No question provided.")
            return
        run_retrieval(query)
        return

    if mode == "answer":
        query = prompt_question()
        if not query:
            print("No question provided.")
            return
        answer_query(query)
        return

    if mode == "multi":
        query = prompt_question()
        if not query:
            print("No question provided.")
            return
        run_multi_query_retrieval(query)
        return

    if mode == "chat":
        run_history_chat_loop()
        return

    if mode == "splitter":
        run_splitter_demo()
        return

    if mode == "all":
        query = prompt_question()
        if not query:
            print("No question provided.")
            return
        run_all_flows(query)
        return

    print("Unknown mode. Use one of: ingest, retrieve, answer, multi, chat, splitter, all")


if __name__ == "__main__":
    main()
