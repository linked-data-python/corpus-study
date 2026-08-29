# Context shim (see meta.json): `timefuncs` (RDFLib/timefuncs@dd3bde87277) is
# not installable here. The real test imports `from timefuncs import
# is_after`, which -- as a side effect of importing the `timefuncs` package
# -- runs `timefuncs/__init__.py` and registers `tfun:isAfter` as a custom
# SPARQL extension function via rdflib's `register_custom_function`. That
# side effect is what this module reproduces: `is_after` and its private
# helper `_path_exists` are copied verbatim from `timefuncs/funcs.py` at the
# commit above (no logic invented -- the real query in the region needs the
# real predicate semantics to reproduce the real `expected` list), and the
# same registration call is issued at import time.
# Identical bindings for both representations.
from typing import List, Tuple, Union
from typing import Literal as TLiteral

from rdflib import BNode, Namespace, URIRef
from rdflib.namespace import TIME
from rdflib.paths import ZeroOrMore
from rdflib.plugins.sparql.operators import register_custom_function

TFUN = Namespace("https://w3id.org/timefuncs/")


def _path_exists(
    g,
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
        next_nodes = []
        for p in preds:
            if p[1] == "outbound":
                for o in g.objects(subject=node, predicate=p[0]):
                    next_nodes.append(o)
            elif p[1] == "inbound":
                for s in g.subjects(predicate=p[0], object=node):
                    next_nodes.append(s)
        return next_nodes

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


def is_after(e, ctx):
    """SPARQL tfun:isAfter(a, b)

    Returns Literal(true) if a is after b where 'after' is determined by all
    of the possibilities for its expression within the Time Ontology in OWL,
    see https://www.w3.org/TR/owl-time/#time:after. Returns Literal(false)
    otherwise.
    """
    from rdflib import Literal

    try:
        a = e.expr[0]
        b = e.expr[1]
    except Exception:
        raise ValueError(
            "This function, isAfter(a, b), requires two IRI parameters, "
            "where a & b are Time Ontology TemporalEntity instances. "
            "a is tested to be before b"
        )

    g = ctx.ctx.graph

    if (a, TIME.hasBeginning * ZeroOrMore / TIME.after, b) in g:
        return Literal(True)

    if (b, TIME.hasEnd * ZeroOrMore / TIME.before, a) in g:
        return Literal(True)

    for z in g.objects(b, TIME.hasEnd * ZeroOrMore / TIME.before):
        if (a, TIME.hasBeginning, z) in g:
            return Literal(True)

    for z in g.objects(a, TIME.hasBeginning * ZeroOrMore / TIME.after):
        if (b, TIME.hasEnd, z) in g:
            return Literal(True)

    ref_xsds = list(
        g.objects(b, TIME.hasBeginning * ZeroOrMore / TIME.inXSDDateTimeStamp)
    )
    x_xsds = list(g.objects(a, TIME.hasEnd * ZeroOrMore / TIME.inXSDDateTimeStamp))
    if len(ref_xsds) > 0 and len(x_xsds) > 0:
        if sorted(x_xsds)[0] > sorted(ref_xsds)[-1]:
            return Literal(True)

    ref_xsds = list(g.objects(b, TIME.hasBeginning * ZeroOrMore / TIME.inXSDDate))
    x_xsds = list(g.objects(a, TIME.hasEnd * ZeroOrMore / TIME.inXSDDate))
    if len(ref_xsds) > 0 and len(x_xsds) > 0:
        if sorted(x_xsds)[0] > sorted(ref_xsds)[-1]:
            return Literal(True)

    if _path_exists(g, a, b, [(TIME.after, "outbound"), (TIME.before, "inbound")]):
        return Literal(True)

    return Literal(False)


register_custom_function(TFUN.isAfter, is_after, raw=True)
