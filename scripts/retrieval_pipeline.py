import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "Utils"))

import script

def looks_like_runner_command(value):
    lower = value.lower()
    return (
        ("python" in lower and (".py" in lower or "python.exe" in lower or "scripts" in lower))
        or "cd /d" in lower
        or "&&" in lower
        or "retrieval_pipeline.py" in lower
        or "-u" in lower
        or value == "--"
    )


def extract_query_from_args():
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
    query = extract_query_from_args()
    if not query:
        query = input("Enter your question: ").strip()

    if not query:
        print("No question provided.")
        return

    script.run_retrieval(query)


if __name__ == "__main__":
    main()