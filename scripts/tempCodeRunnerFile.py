try:
    import script
except ImportError:
    raise ImportError("Could not locate script.py. Ensure it is placed inside the 'Utils' directory.")
