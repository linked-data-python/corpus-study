"""Validation driver for BrickSchema__Brick__tests_test_subclass_hierarchy.py__test_cycles.

`test_cycles()` reads a module-global `g` in the extracted region -- no
parameter, no visible RDF op until you notice the global (rdf_ops: 0 in
meta.json). The signature gained a `g=g` default so `run_pair(fixture=...)`
can hand it a fresh graph per side: the "annotated parameter" remedy
AGENT_BATCH.md prescribes for this shape of region. The function BODY is
byte-for-byte the extracted original; only the parameter list changed, and
identically on both sides.

See meta.json's translation_notes for why the loop holding the term
interpolation under study (`{brick_class}`) cannot be exercised through
run_pair without breaking its exception model, and what this driver DOES
still prove.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_cycles',
    fixture="fixture.ttl",
)
