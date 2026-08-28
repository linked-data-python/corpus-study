"""Validation driver for test_diff_validation.

Module-state comparison: the demo harness at the end of both files runs the
region (whose own ``pytest.raises`` assertions check that the two named
graph IRIs land in the right guard) and exposes what the store ended up
holding as the module-level Graph ``recorded``, which the harness compares
by isomorphism.

``NeatInstanceStore`` / ``NeatValueError`` are the stand-ins from
``neat_context`` -- see that module for why the real ``cognite.neat``
cannot run here.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
