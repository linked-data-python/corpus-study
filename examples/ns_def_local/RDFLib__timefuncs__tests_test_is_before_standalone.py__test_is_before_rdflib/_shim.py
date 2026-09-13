# Context shim (see meta.json): subset of tests/test_is_before_standalone.py
# from RDFLib/timefuncs@dd3bde8727, so the region executes outside the
# package. Identical bindings for both representations.
from pathlib import Path
from typing import List, Tuple, Union
from typing import Literal as TLiteral
from rdflib import Graph, TIME, URIRef, BNode
from rdflib.paths import ZeroOrMore, OneOrMore

tests_dir = Path(__file__).parent


def is_before_rdflib(g: Graph, a, b):
    for s, o in g.subject_objects(TIME.before):
        g.add((o, TIME.after, s))

    # ?x time:hasEnd?/time:before ?ref .
    if (a, TIME.hasEnd * ZeroOrMore / TIME.before * OneOrMore, b) in g:
        return True

    # ?ref time:hasBeginning?/time:after ?x .
    if (b, TIME.hasBeginning * ZeroOrMore / TIME.after * OneOrMore, a) in g:
        return True

    # ?ref time:hasBeginning?/time:after ?z .
    # ?x time:hasEnd ?z .
    for z in g.objects(b, TIME.hasBeginning * ZeroOrMore / TIME.after):
        if (a, TIME.hasEnd, z) in g:
            return True

    # ?ref time:hasBeginning ?z .
    # ?x time:hasEnd?/time:before ?z .
    for z in g.objects(b, TIME.hasBeginning):
        if (a, TIME.hasEnd * ZeroOrMore / TIME.before, z) in g:
            return True

    # ?ref time:hasBeginning?/time:inXSDDateTimeStamp ?refXSD .
    # ?x time:hasEnd?/time:inXSDDateTimeStamp ?xXSD .
    # FILTER (?xXSD < ?refXSD)

    # if the latest date of x is smaller than the earliest date of ref...
    ref_xsds = list(g.objects(b, TIME.hasBeginning * ZeroOrMore / TIME.inXSDDateTimeStamp))
    x_xsds = list(g.objects(a, TIME.hasEnd * ZeroOrMore / TIME.inXSDDateTimeStamp))
    if len(ref_xsds) > 0 and len(x_xsds) > 0:
        if sorted(x_xsds)[-1] < sorted(ref_xsds)[0]:
            return True

    if _path_exists(g, a, b, [(TIME.before, "outbound"), (TIME.after, "inbound")]):
        return True

    return False


def _path_exists(
    g: Graph,
    a: Union[URIRef, BNode],
    b: Union[URIRef, BNode],
    predicates: List[Tuple[URIRef, TLiteral["outbound", "inbound"]]],
) -> bool:
    """Finds if any path between RDF nodes a and b in graph g exists,
    following any of the predicates supplied, in any order.

    This function is a support function for the names TIME functions such as is_before."""

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
