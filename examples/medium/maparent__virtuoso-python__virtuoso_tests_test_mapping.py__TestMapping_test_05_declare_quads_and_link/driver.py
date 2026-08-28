"""Validation driver for maparent__virtuoso-python ... test_05_declare_quads_and_link.

The region is a test method that reads the module-level `session`, so the
`self` stand-in has to be built inside each module: both sides carry an
identical demo-harness section (see meta.json) that calls the method and
exposes the resulting named graph as DEMO_GRAPH.  entry=None compares that
graph by isomorphism plus the captured stdout.

The one term the translation changes is TST.alink / tst:alink, and the
region's own assertion (`graph.triples((None, TST.alink, None))` must be
non-empty) fails loudly if the two do not denote the same IRI.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
