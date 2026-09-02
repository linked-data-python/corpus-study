"""Validation driver for
ktbs__ktbs__utest_test_ktbs_method_fsa.py__TestFSAAsk_test_no_match_V.

EXCLUDED (see meta.json). Unlike the ns_import_project sibling for
lib/ktbs/methods/hrules.py (do_compute_obsels), THIS region's own body has
no direct `rdfrest` import, so -- once `ktbs.namespace` is restored via
ktbs_namespace_context.py (needed anyway: the real `ktbs.namespace` itself
imports `rdfrest.cores.local`, and `rdfrest` is not on PyPI at all --
verified: `~/.venvs/ldpy/bin/pip index versions rdfrest` -> "No matching
distribution found") -- BOTH original.py and translated.ldpy import
cleanly. The failure instead happens at CALL time: `test_no_match_V(self)`
is a bound test method extracted from `TestFSAAsk(TestFSA(KtbsTestCase))`
in utest/test_ktbs_method_fsa.py, and its body dereferences `self.base`,
`self.src`, `self.otypeA`, `self.atypeV`, `self.base_structure`,
`self.model_dst` -- all set up by `TestFSA.setup_method` /
`TestFSAAsk`'s own setup (verified against the real file), themselves
built through a live in-memory kTBS engine (`self.my_ktbs.create_base(...)`
etc.) on top of `KtbsTestCase` (utest/test_ktbs_engine.py), which in turn
needs `rdfrest` -- not installed, not installable (not on PyPI).

There is no `self` fixture this driver can construct without
re-implementing kTBS's obsel-collection / computed-trace machinery well
enough that `create_computed_trace(..., KTBS.fsa, ...)` actually runs the
finite-state-automaton method over the source obsels and decides whether
`ctr.obsels` gains any -- which is precisely the behaviour under test, and
reproducing it is forbidden by AGENT_BATCH ("n'inventez pas de logique"),
the same call made for this stratum's do_compute_obsels sibling. So the
call below passes a bare stand-in with none of those attributes: it fails
identically and for the same reason on both sides (an AttributeError on
`self.base`), which is the honest result -- not a workaround for it.

The one real ns_import_project rewrite here -- `from ktbs.namespace import
KTBS, KTBS_NS_URI` -> `from ktbs_namespace_context import KTBS_NS_URI,
ktbs:`, `KTBS.fsa` -> `ktbs:fsa` -- transpiles cleanly (verified directly:
`python -m ldpy.transpiler` on translated.ldpy) and is not in doubt; what
cannot be established is whether the REGION as a whole still behaves
identically, because neither side can be driven past needing the live
kTBS test engine.
"""
import types

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_no_match_V',
    calls=[((types.SimpleNamespace(),), {})],  # bare `self`: fails
                                                # identically on both sides
                                                # at `self.base`, before any
                                                # RDF operation is reached
)
