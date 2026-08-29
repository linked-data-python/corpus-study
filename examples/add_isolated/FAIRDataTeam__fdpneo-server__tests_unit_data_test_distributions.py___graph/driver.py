"""Validation driver for FAIRDataTeam__fdpneo-server__tests_unit_data_test_distributions.py___graph.

The region BUILDS and returns a fresh graph, so the oracle is RDF
isomorphism (meta.oracle == "isomorphism"), on the returned value.

Three cases exercise the three independent boolean flags that each gate
one of the region's three conditional +{ } / .add() sites, on top of the
unconditional marker triple: all default (True/True/True), all off (only
the marker triple survives), and a mix (so no single flag's effect is
confused with another's).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="_graph",
    calls=[
        lambda: ((), {}),
        lambda: ((), {"with_download": False, "with_access": False,
                       "with_rights": False}),
        lambda: ((), {"with_download": True, "with_access": False,
                       "with_rights": True}),
    ],
)
