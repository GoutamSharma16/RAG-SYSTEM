import sys

from script import (
    get_chat_model,
    get_vector_store,
    history_aware_answer,
    run_history_chat_loop,
)


def looks_like_runner_command(value):
    """Detect launch-command noise so the wrapper prompts the user for the real question."""
    lower = value.lower()
    return (
        ("python" in lower and (".py" in lower or "python.exe" in lower or "scripts" in lower))
        or "cd /d" in lower
        or "&&" in lower
        or "history_aware_generation.py" in lower
        or "-u" in lower
        or value == "--"
    )


def extract_query_from_args():
    """Ignore Python runner flags so the script can prompt for the original question."""
    cleaned_args = []
    for arg in sys.argv[1:]:
        if not arg or arg == "--" or arg.startswith("-"):
            continue
        if looks_like_runner_command(arg):
            continue
        cleaned_args.append(arg)

    query = " ".join(cleaned_args).strip()
    return query or None


def ask_question(user_question, db, model, chat_history):
    """Compatibility wrapper that preserves the function signature used by the older file."""
    return history_aware_answer(user_question, db, model, chat_history)


def start_chat():
    """Compatibility wrapper for the interactive history-aware chat loop."""
    run_history_chat_loop()


def main():
    """Compatibility wrapper for the history-aware generation flow."""
    query = extract_query_from_args()
    if query:
        db = get_vector_store()
        model = get_chat_model()
        chat_history = []
        ask_question(query, db, model, chat_history)
        return

    start_chat()


if __name__ == "__main__":
    main()
