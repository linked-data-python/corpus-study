"""Validation driver for linkml's ShaclIfAbsentProcessor module.

The region is a whole module defining one class, so there is nothing
observable at import time.  Both files therefore end with the same demo
harness: it instantiates the processor against a stand-in SchemaView, calls
every mapping method, and collects the resulting RDF terms into
`demo_graph` (compared by isomorphism) plus two printed lines (stdout is
compared too).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
