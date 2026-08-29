"""Validation driver for AtomGraph__Web-Algebra__tests_unit_test_values.py___two_var_two_rows.

The region builds its own two-triple graph (no external input) before
querying it, so there is nothing to inject through a `fixture.ttl`:
`_two_var_two_rows()` takes no argument.  The oracle is still the equality
of the *values* the query returns, not isomorphism -- the region's whole
point is the SELECT it runs, not the graph it built to run it against.

`calls=[((), {})]` invokes the entry point once per side, with no arguments.
`ordered=True` because the region's own query asks for `ORDER BY ?s`.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='_two_var_two_rows',
    calls=[((), {})],
    ordered=True,
)
