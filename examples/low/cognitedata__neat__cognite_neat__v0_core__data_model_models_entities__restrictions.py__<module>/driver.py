"""Validation driver for cognite.neat's _restrictions.py.

Module-level region: it defines pydantic models and a parse_restriction()
entry point, so nothing is observable at import time.  Both representations
therefore end with an identical demo harness (see meta.json) that parses the
five restriction shapes the module supports -- including the datatyped-literal
one, which is the region's single RDF term construction and the only place a
translation was possible -- and prints the round-tripped strings plus the
Literal itself.  The harness compares the captured stdout.

Context shim: neat_shim.py provides behavioural stand-ins for the six names the
region imports from cognite.neat (whose package __init__ needs the whole
cognite-client SDK).  It is imported identically by both representations, which
run in this same process.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
