"""Validation driver for ktbs__ktbs__lib_ktbs_api_trace.py__StoredTraceMixin_set_trace_begin_dt.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
import contextlib

from rdflib import Graph, URIRef
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair


class _FakeTrace:
    """Minimal stand-in for StoredTraceMixin: only what the region touches
    (``self.uri``, ``self.edit()`` yielding an editable graph)."""

    def __init__(self):
        self.uri = URIRef("http://example.org/trace1")
        self.graph = Graph()
        self.graph.add((self.uri, URIRef("http://liris.cnrs.fr/silex/2009/ktbs#hasTraceBegin"),
                         URIRef("http://example.org/obsel1")))

    @contextlib.contextmanager
    def edit(self):
        yield self.graph

    def __eq__(self, other):
        return isinstance(other, _FakeTrace) and \
            to_isomorphic(self.graph) == to_isomorphic(other.graph)


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='set_trace_begin_dt',
    calls=[lambda: ((_FakeTrace(), "2024-01-01T00:00:00"), {})],
)
