import sys

from scripts import run_multi_query_retrieval


def looks_like_runner_command(value):
    """Detect launch-command noise so the wrapper prompts the user for the real question."""
    lower = value.lower()
    return (
        ("python" in lower and (".py" in lower or "python.exe" in lower or "scripts" in lower))
        or "cd /d" in lower
        or "&&" in lower
        or "multi_query_retrieval.py" in lower
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


def main():
    """Compatibility wrapper for the consolidated single-file launcher."""
    query = extract_query_from_args()
    if not query:
        query = input("Enter your question: ").strip()

    if not query:
        print("No question provided.")
        return

    run_multi_query_retrieval(query)


if __name__ == "__main__":
    main()