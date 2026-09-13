"""Validation driver for kumagallium__asterism__api_tests_test_orphan_reclaim_api.py___add_version.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
import rdflib
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair


class _DatasetHolder:
    """Wraps an ``rdflib.Dataset``: NOT a ``Graph`` subclass, so the harness
    falls through to ``__eq__`` instead of trying isomorphism on the whole
    (multi-context) dataset, which ``rdflib.compare.to_isomorphic`` cannot
    handle (it iterates quads, not triples)."""

    def __init__(self):
        self.ds = rdflib.Dataset()

    def graph(self, identifier):
        return self.ds.graph(identifier)

    def __eq__(self, other):
        if not isinstance(other, _DatasetHolder):
            return NotImplemented
        a = {str(c.identifier): to_isomorphic(c)
             for c in self.ds.contexts() if len(c)}
        b = {str(c.identifier): to_isomorphic(c)
             for c in other.ds.contexts() if len(c)}
        return a == b


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_add_version',
    calls=[lambda: ((_DatasetHolder(), "http://example.org/g1"), {})],
)
