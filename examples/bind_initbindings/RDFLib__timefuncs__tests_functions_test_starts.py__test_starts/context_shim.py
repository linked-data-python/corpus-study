# Context shim (see meta.json): the real test does `from timefuncs import
# starts`, which -- through timefuncs/__init__.py's module-level side
# effect -- registers `tfun:starts` as a SPARQL extension function via
# `register_custom_function`. `timefuncs` is not installed in the pinned
# study venv (the study venv is pinned; the package is not on PyPI there),
# so this shim transcribes VERBATIM the two pieces of
# RDFLib/timefuncs@dd3bde8727 the test actually exercises:
# `timefuncs/funcs.py`'s `starts` and its BFS helper `_path_exists`, and
# the one `register_custom_function` call from `timefuncs/__init__.py` that
# wires `starts` to `tfun:starts`. Both functions only import from
# `rdflib` and the standard library. Identical for both representations
# (same convention as the test_finishes region elsewhere in this stratum).
from typing import List, Tuple
from typing import Literal as TLiteral
from typing import Union

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, TIME
from rdflib.namespace import Namespace
from rdflib.plugins.sparql.operators import register_custom_function


def _path_exists(
    g: Graph,
    a: Union[URIRef, BNode],
    b: Union[URIRef, BNode],
    predicates: List[Tuple[URIRef, TLiteral["outbound", "inbound"]]],
) -> bool:
    """Finds if any path between RDF nodes a and b in graph g exists,
    following any of the predicates supplied, in any order.

    This function is a support function for the named TIME functions such as is_before."""

    if a == b:
        return False

    def _get_next_nodes(node, preds):
        """Finds any nodes linked to a given node, 'node' via any of the given predicates 'pred'.

        Looks for both s pred o and o pred s (inverse)"""
        next_nodes = []

        for p in preds:
            if p[1] == "outbound":
                for o in g.objects(subject=node, predicate=p[0]):
                    next_nodes.append(o)
            elif p[1] == "inbound":
                for s in g.subjects(predicate=p[0], object=node):
                    next_nodes.append(s)

        return next_nodes

    # standard breadth-first search
    def bfs(node):
        visited = []
        queue = []
        visited.append(node)
        queue.append(node)

        while queue:
            s = queue.pop(0)
            for x in _get_next_nodes(s, predicates):
                if x == b:
                    return True
                if x not in visited:
                    visited.append(x)
                    queue.append(x)
        return False

    return bfs(a)


def starts(e, ctx) -> Literal:
    """SPARQL tfun:starts(a, b)

    From https://www.w3.org/TR/owl-time/#time:intervalStarts:
    "If a proper interval T1 is intervalStarts another proper interval T2, then the beginning of T1 is coincident
    with the beginning of T2, and the end of T1 is before the end of T2. "

    Returns Literal(true) if a and be are ProperIntervals and the beginning of a is coincident with the beginning
    of b, and the end of a is before the end of b. Else returns False.

    tfun:starts(a, b) is equivalent to tfun:isStartedBy(b, a)
    """
    try:
        a = e.expr[0]
        b = e.expr[1]
    except Exception as err:
        raise ValueError(
            "This function, isInside(a, b), requires two IRI parameters, "
            "where a & b are Time Ontology Instant and Interval instances, respectively. "
            "a is tested to be inside b"
        )

    g = ctx.ctx.graph

    # a must be some form of Interval
    if (a, RDF.type, TIME.Interval) not in g and (a, RDF.type, TIME.ProperInterval) not in g:
        return Literal(False)

    # b must be some form of Interval
    if (b, RDF.type, TIME.Interval) not in g and (b, RDF.type, TIME.ProperInterval) not in g:
        return Literal(False)

    # direct or transitive declared relations
    if _path_exists(
        g, a, b, [
                (TIME.intervalStarts, "outbound"), (TIME.intervalStartedBy, "inbound"),
                (TIME.intervalEquals, "outbound"), (TIME.intervalEquals, "inbound")
            ]
    ):
        return Literal(True)

    # the beginning of a is coincident with the beginning of b, and the end of a is before the end of b
    for o in g.objects(a, TIME.hasBeginning):
        for a_beg in g.objects(o, TIME.inXSDDateTimeStamp):
            for o2 in g.objects(b, TIME.hasBeginning):
                for b_beg in g.objects(o2, TIME.inXSDDateTimeStamp):
                    for o3 in g.objects(a, TIME.hasEnd):
                        for a_end in g.objects(o3, TIME.inXSDDateTimeStamp):
                            for o4 in g.objects(b, TIME.hasEnd):
                                for b_end in g.objects(o4, TIME.inXSDDateTimeStamp):
                                    if a_beg == b_beg and a_end < b_end and a_beg < a_end and b_beg < b_end:
                                        return Literal(True)

    return Literal(False)


TFUN = Namespace("https://w3id.org/timefuncs/")
register_custom_function(TFUN.starts, starts, raw=True)
