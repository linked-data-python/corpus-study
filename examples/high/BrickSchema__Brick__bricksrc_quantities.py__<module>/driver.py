"""Validation driver for BrickSchema__Brick__bricksrc_quantities.py__<module>.

The region is a data module: it declares `quantity_definitions`, a nested dict
whose keys are RDF predicates, and never turns it into triples itself (Brick's
generate_brick.py does).  Both sides therefore carry an identical demo-harness
section (see meta.json) that walks the structure into DEMO_GRAPH, so that
entry=None compares every one of the 78 terms by graph isomorphism, plus the
empty `g` the module builds and the captured stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
