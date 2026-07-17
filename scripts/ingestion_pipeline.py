import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, "Utils"))

import script

def main():
    """Runs data parsing logic synchronously."""
    script.run_ingestion()


if __name__ == "__main__":
    main()