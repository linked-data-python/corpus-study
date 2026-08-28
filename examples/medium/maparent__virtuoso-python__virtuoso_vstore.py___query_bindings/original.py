# Extracted from maparent/virtuoso-python@eba377e1fa : virtuoso/vstore.py
# region: _query_bindings (lines 730-753, band medium)
# licence of the source repository: see meta.json
from rdflib.graph import Graph
from rdflib.term import URIRef, BNode, Literal, Variable

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
