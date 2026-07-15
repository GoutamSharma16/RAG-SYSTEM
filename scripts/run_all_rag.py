from script import run_all_flows


def looks_like_runner_command(value):
    """Detect shell or Python runner command noise that should not become a user question."""
    lower = value.strip().lower()
    if not lower:
        return True

    return (
        "cd /d" in lower
        or "&&" in lower
        or "run_all_rag.py" in lower
        or "python.exe" in lower
        or "venv\\scripts\\python.exe" in lower
        or "-u" in lower
        or value.strip() == "--"
    )


def main():
    """Prompt-first interactive wrapper around the consolidated RAG launcher."""
    print("Ask me questions! Type 'quit' to exit.")

    while True:
        question = input("\nYour question: ")

        if question.lower() == "quit":
            print("Goodbye!")
            break

        if not question.strip():
            print("No question provided.")
            continue

        if looks_like_runner_command(question):
            print("Please type your actual question.")
            continue

        run_all_flows(question)


if __name__ == "__main__":
    main()
