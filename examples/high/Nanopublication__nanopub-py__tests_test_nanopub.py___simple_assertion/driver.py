"""Validation driver: _simple_assertion builds and returns a fresh Graph."""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="_simple_assertion",
                   calls=[lambda: ((), {})])
