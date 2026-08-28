# Context shim (see meta.json): the bindings that app/run_search.py of
# JustlyAI/lmss_entity_extractor@6acc4d8389 defines *above* the extracted line
# range and that the region still uses (LMSS_DIR, load_top_classes, the logging
# setup).  load_top_classes and the logging.basicConfig call are copied
# verbatim from lines 16-25 of the upstream file; only LMSS_DIR is retargeted
# at this example directory, which holds the miniature fixture files.
# Identical for both representations.
import json
import logging
from pathlib import Path
from typing import List

LMSS_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(asctime)s - %(message)s"
)


def load_top_classes(file_path: Path) -> List[str]:
    with open(file_path, "r") as f:
        top_classes_data = json.load(f)
    return [cls["iri"] for cls in top_classes_data]
