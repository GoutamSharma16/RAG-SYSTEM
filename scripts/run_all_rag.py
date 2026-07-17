import os
import sys
from dotenv import load_dotenv

# 1. Debug where Python is looking for your .env file
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
expected_env_path = os.path.join(project_root, ".env")

print(f"\n[DEBUG] Project Root detected as: {project_root}")
print(f"[DEBUG] Looking for .env at: {expected_env_path}")
print(f"[DEBUG] Does .env exist there? {'YES' if os.path.exists(expected_env_path) else 'NO'}")

# Explicitly load from the absolute path
load_dotenv(expected_env_path)

# Confirm if the key actually loaded into memory
has_key = "OPENROUTER_API_KEY" in os.environ
print(f"[DEBUG] Was OPENROUTER_API_KEY loaded successfully? {'YES' if has_key else 'NO'}\n")

# 2. Setup script imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, "Utils"))

try:
    import script
except ImportError:
    raise ImportError("Could not locate script.py. Ensure it is placed inside the 'Utils' directory.")


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

        script.run_all_flows(question)


if __name__ == "__main__":
    main()