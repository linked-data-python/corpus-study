# Context shim (see meta.json): minimal stand-in for models/locations.py
# from TheWorldAvatar/mcp-tool-layer@c440a33e08 (repository root, not under
# src/) -- the real module resolves DATA_DIR relative to the repository
# root, loads a .env file via python-dotenv, and raises FileNotFoundError
# at IMPORT time if a handful of real directories (RAW_DATA_DIR,
# CONFIGS_DIR, ...) do not exist on disk. None of that machinery is part of
# what this region reads: only the VALUE of DATA_DIR matters, as the
# directory under which `<hash_value>/ontomops_extension.ttl` is looked up.
# Resolved here as a fixed path next to this shim (`data/`, sibling of the
# `models/` package, committed alongside fixture.ttl -- see driver.py and
# meta.json for why the fixture is duplicated there). Identical for both
# representations.
import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
