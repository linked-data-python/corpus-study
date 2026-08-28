"""Validation driver for landrs-toolkit__PySOSA__PySOSA_Actuator.py__Actuator___init__.

The region writes into the module-level `obsgraph` and returns nothing, so the
pair is compared in module-state mode, driven by the demo harness both files
carry.  `PySOSA` is made importable from the corpus checkout of the pinned
commit, so the region's imports stay exactly as upstream.

config.get_graph() upstream hands out one module-level Graph; since the harness
runs both modules in the same process they would share -- and accumulate into
-- it, which would make the comparison vacuous.  It is replaced here by a
factory returning a fresh Graph, identically for both sides.
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_REPO = (Path(__file__).resolve().parents[3]
         / "corpus" / "repos" / "landrs-toolkit__PySOSA")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from rdflib import Graph          # noqa: E402
from PySOSA import config as cfg  # noqa: E402

cfg.get_graph = lambda: Graph()

from rdfeval.harness import run_pair  # noqa: E402

VERDICT = run_pair(__file__, entry=None, calls=None)
