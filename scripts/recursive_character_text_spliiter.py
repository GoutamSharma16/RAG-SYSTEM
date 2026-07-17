import os
import sys

# Get the path to the main project directory and append the Utils folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "Utils"))

try:
    from script import run_splitter_demo
except ImportError:
    raise ImportError("Could not locate script.py. Ensure it is placed inside the 'Utils' directory.")


def main():
    """Compatibility wrapper for the consolidated single-file launcher."""
    run_splitter_demo()


if __name__ == "__main__":
    main()