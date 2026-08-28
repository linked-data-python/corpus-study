"""Validation driver for kif_lib/namespace/wikidata.py.

Module-level region.  It only *defines* namespaces (a class full of
rdflib Namespace constants and lookup tables), so nothing would be observable
at import time; both representations therefore end with an identical demo
harness (see meta.json) that builds a small graph with those namespaces and
prints a few derived values.  The harness compares the resulting demo_graph by
isomorphism plus the captured stdout -- which includes str(Wikidata.PREFERRED)
& co., i.e. exactly the three constants the translation turned into prefixed
name islands.

Context shims (identical for both representations, same process):
  * kif_shim.py stands for kif_lib's `..rdflib` / `..typing` re-export modules;
  * wikibase.py is the reduced kif_lib/namespace/wikibase.py (original.py only;
    translated.ldpy expresses those three terms as wikibase: islands).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
