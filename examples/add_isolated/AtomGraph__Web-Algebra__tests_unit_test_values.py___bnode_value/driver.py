"""Validation driver for AtomGraph__Web-Algebra__tests_unit_test_values.py___bnode_value.

_bnode_value takes NO arguments: it builds its own graph internally (a single
isolated `g.add((s, p, o))`) and returns the result of querying it. There is
no external input graph, so the reading oracle's `fixture=` (which parses a
Turtle file and passes it as the entry point's sole argument) does not apply
here -- the oracle is simply "same values out of a no-argument call",
compared as a materialised multiset (no store promises an order for a bare
`?o` projection).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='_bnode_value',
    calls=[((), {})],
    ordered=False,
)
