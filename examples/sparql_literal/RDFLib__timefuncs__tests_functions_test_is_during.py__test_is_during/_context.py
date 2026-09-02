# Context shim (see meta.json): `timefuncs` (RDFLib/timefuncs@dd3bde87277) is
# not installable here. The real test imports `from timefuncs import
# is_during`, which -- as a side effect of importing the `timefuncs` package
# -- runs `timefuncs/__init__.py` and registers `tfun:isDuring` as a custom
# SPARQL extension function via rdflib's `register_custom_function`. That
# side effect is what this module reproduces: `is_during`, the private
# helper `is_contained_by` it delegates to, and `is_contained_by`'s own
# helper `_path_exists` are copied verbatim from `timefuncs/funcs.py` at the
# commit above (no logic invented -- the real query in the region needs the
# real predicate semantics to reproduce solutions against real data), and
# the same registration call is issued at import time.
# Identical bindings for both representations.
from typing import List, Tuple, Union
from typing import Literal as TLiteral

from rdflib import BNode, Namespace, URIRef
from rdflib.namespace import TIME
from rdflib.paths import OneOrMore
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


def is_contained_by(e, ctx):
    """SPARQL tfun:isContainedBy(a, b)

    Returns Literal(true) if a is contained by b where 'is contained by' is
    determined by all of the possibilities for calculating the predicate
    `time:intervalDuring` in the Time Ontology in OWL, see
    https://www.w3.org/TR/owl-time/#time:intervalDuring. Returns
    Literal(false) otherwise.

    Note that this function calculates the inverse to the function contains().
    """
    from rdflib import Literal

    try:
        a = e.expr[0]
        b = e.expr[1]
    except Exception:
        raise ValueError(
            "This function, isInside(a, b), requires two IRI parameters, "
            "where a & b are Time Ontology Instant and Interval instances, respectively. "
            "a is tested to be inside b"
        )

    g = ctx.ctx.graph

    if (a, TIME.intervalDuring * OneOrMore, b) in g:
        return Literal(True)

    if (b, TIME.intervalContains * OneOrMore, a) in g:
        return Literal(True)

    for a_beginning in g.objects(a, TIME.hasBeginning):
        for a_end in g.objects(a, TIME.hasEnd):
            for b_beginning in g.objects(b, TIME.hasBeginning):
                for b_end in g.objects(b, TIME.hasEnd):
                    # declared
                    if (a_beginning, TIME.after, b_beginning) in g and (
                        a_end,
                        TIME.before,
                        b_end,
                    ) in g:
                        return Literal(True)
                    if (b_beginning, TIME.before, a_beginning) in g and (
                        a_end,
                        TIME.before,
                        b_end,
                    ) in g:
                        return Literal(True)
                    if (b_beginning, TIME.before, a_beginning) in g and (
                        b_end,
                        TIME.after,
                        a_end,
                    ) in g:
                        return Literal(True)
                    if (a_beginning, TIME.after, b_beginning) in g and (
                        b_end,
                        TIME.after,
                        a_end,
                    ) in g:
                        return Literal(True)

                    # calculated
                    for a_beginning_time in g.objects(
                        a_beginning,
                        TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate,
                    ):
                        for a_end_time in g.objects(
                            a_end,
                            TIME.inXSDDateTimeStamp
                            | TIME.inXSDDateTime
                            | TIME.inXSDDate,
                        ):
                            for b_beginning_time in g.objects(
                                b_beginning,
                                TIME.inXSDDateTimeStamp
                                | TIME.inXSDDateTime
                                | TIME.inXSDDate,
                            ):
                                for b_end_time in g.objects(
                                    b_end,
                                    TIME.inXSDDateTimeStamp
                                    | TIME.inXSDDateTime
                                    | TIME.inXSDDate,
                                ):
                                    if (
                                        b_beginning_time < a_beginning_time
                                        and a_end_time < b_end_time
                                    ):
                                        return Literal(True)

    if _path_exists(
        g, a, b, [(TIME.intervalDuring, "outbound"), (TIME.intervalContains, "inbound")]
    ):
        return Literal(True)

    return Literal(False)


def is_during(e, ctx):
    """SPARQL tfun:isDuring(a, b)

    Alias for is_contained_by."""
    return is_contained_by(e, ctx)


register_custom_function(TFUN.isDuring, is_during, raw=True)
