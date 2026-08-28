"""Context shim for the ``Virtuoso.contexts`` region.

Two things are provided:

* ``_query_bindings`` / ``_bnode_to_nodeid``: module-level helpers the region
  calls, copied verbatim from maparent/virtuoso-python@eba377e1fa
  ``virtuoso/vstore.py`` lines 625-633 and 730-753 (BSD-3, see COPYRIGHT in
  the corpus checkout).

* ``FakeVirtuosoStore``: a stand-in for the ``Virtuoso`` store the method is a
  method of.  The real one talks to a Virtuoso server over ODBC, which the
  evaluation cannot do; this one is an rdflib ``Store`` (so that
  ``Graph(self, URIRef(uri))`` builds a real Graph), records the SQL/SPARQL
  text the region hands to the cursor and replays a fixed row set.  It stands
  in for the *context* of the region, never for the region itself, and
  ``original.py`` and ``translated.ldpy`` use it identically.
"""

from rdflib.graph import Graph
from rdflib.store import Store
from rdflib.term import BNode, URIRef, Variable


def _bnode_to_nodeid(bnode):
    from string import ascii_letters
    iri = bnode
    for c in bnode[1:]:
        if c in ascii_letters:
            # from rdflib not virtuoso
            iri = "b" + "".join(str(ord(x) - 38) for x in bnode[:8])
            break
    return URIRef("nodeID://%s" % iri)


def _query_bindings(triple, g=None, to_n3=True):
    (s, p, o) = triple
    if isinstance(g, Graph):
        g = g.identifier
    if s is None: s = Variable("S")
    if p is None: p = Variable("P")
    if o is None: o = Variable("O")
    if g is None: g = Variable("G")
    if isinstance(s, BNode):
        s = _bnode_to_nodeid(s)
    if isinstance(p, BNode):
        p = _bnode_to_nodeid(p)
    if isinstance(o, BNode):
        o = _bnode_to_nodeid(o)
    if isinstance(g, BNode):
        g = _bnode_to_nodeid(g)
    if to_n3:
        return dict(
            zip("SPOG", [x.n3() for x in (s, p, o, g)])
        )
    else:
        return dict(
            zip("SPOG", [x for x in (s, p, o, g)])
        )


class _RecordingCursor:
    """Minimal stand-in for the pyodbc cursor `Virtuoso.cursor()` returns."""

    def __init__(self, store):
        self._store = store

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, q):
        self._store.queries.append(q)
        return [(uri,) for uri in self._store.uris]


class FakeVirtuosoStore(Store):
    """Enough of the Virtuoso store for `contexts` to run off-line."""

    context_aware = True

    def __init__(self, uris, quad_storage=None):
        super(FakeVirtuosoStore, self).__init__()
        self.uris = list(uris)
        self.quad_storage = quad_storage
        self.queries = []

    def cursor(self):
        return _RecordingCursor(self)
