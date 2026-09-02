"""Validation driver for dice-group__COVID19DS__decaData_product_purchasing_toRdf.py__handleFile.

Establishes semantic equivalence of original.py and translated.ldpy.

handleFile() takes no argument and returns nothing: it mutates the
module-level graph `g` (closure over a global, not a parameter), so the
entry-mode comparison (which only looks at a call's return value, its
mutated args/kwargs and stdout) would see nothing to compare and report a
hollow pass. Both original.py and translated.ldpy therefore carry an
identical "demo harness" appendix (see meta.json) that calls handleFile()
once at module level, so entry=None / module-state comparison picks up `g`
by name and compares it by graph isomorphism -- the same pattern as
examples/remove/DataDrivenCPS__acquirium__.../driver.py.

The input CSV (COVID19_INDEX_SAMPLE_....csv, alongside this driver) and the
context shim (context_shim.py: pandas, OrderedDict, repl()) are read by both
representations identically; see meta.json.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
