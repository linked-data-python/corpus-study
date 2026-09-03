"""Validation driver for BONSAMURAIS/arborist setup_empty_graph.

The region's whole effect is invisible to a triple comparison: it sets
nineteen module globals and binds nineteen prefixes on a graph whose triples
come from a helper. `demo()` — identical in both files — returns the three
things that ARE the region's output: the graph's prefix bindings, the globals
it exports, and the triples.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry='demo', calls=[((), {})])
