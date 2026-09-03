"""Validation driver for bloodbee/jrt teapot_ontology_graph.

The region is a pytest fixture: `@pytest.fixture` wraps the function, so the
entry point cannot be called directly. `demo()` — identical on both sides —
calls the undecorated body through the wrapper's `__wrapped__` and returns
the graph, which the harness compares by isomorphism.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry='demo', calls=[((), {})])
