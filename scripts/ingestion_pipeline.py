from real_rag import run_ingestion


def main():
    """Compatibility wrapper that preserves the legacy entrypoint behavior."""
    run_ingestion()


if __name__ == "__main__":
    main()

