"""Validation driver for dice-group__COVID19DS__acaps-covid19-government-measures_toRdf.py__<module>_64.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is module-level statement code: it fills the module-level graph `g`
and prints one line per row, so the pair is compared in module-state mode
(RDF isomorphism of `g`, plus captured stdout).

Both representations read their rows from the context shim `context_shim.py`,
which restores the two bindings the enclosing script provides (`pd` and
`xls`) and hands out a fresh copy of the table per call -- the region mutates
`row['LINK']`.  The rows are chosen to exercise the four `remove` calls: each
of the four "unknown" datatypes occurs at least once.  See meta.json.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
