# Extracted from RDFLib/timefuncs@dd3bde8727 : timefuncs/funcs.py
# region: finishes (lines 138-201, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import RDF, TIME

def finishes(e, ctx) -> Literal:
    """SPARQL tfun:finishes(a, b)

    From https://www.w3.org/TR/owl-time/#time:intervalFinishes:
    "If a proper interval T1 is intervalFinishes another proper interval T2, then the beginning of T1 is after the
    beginning of T2, and the end of T1 is coincident with the end of T2."

    Returns Literal(true) if a and be are ProperIntervals and the beginning of a is after the beginning of b,
    and the end of a is coincident with the end of b. Else returns False.

    Example:

    SELECT ?a ?b
    WHERE {
        ?a a time:ProperInterval .
        ?b a time:ProperInterval .

        FILTER tfun:finishes(?a, ?b)
    }

    tfun:finishes(a, b) is equivalent to tfun:isFinishedBy(b, a)
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
                (TIME.intervalFinishes, "outbound"), (TIME.intervalFinishedBy, "inbound"),
                (TIME.intervalEquals, "outbound"), (TIME.intervalEquals, "inbound")
            ]
    ):
        return Literal(True)

    # the beginning of T1 is after the beginning of T2, and the end of T1 is coincident with the end of T2
    for o in g.objects(a, TIME.hasBeginning):
        for a_beg in g.objects(o, TIME.inXSDDateTimeStamp):
            for o2 in g.objects(b, TIME.hasBeginning):
                for b_beg in g.objects(o2, TIME.inXSDDateTimeStamp):
                    for o3 in g.objects(a, TIME.hasEnd):
                        for a_end in g.objects(o3, TIME.inXSDDateTimeStamp):
                            for o4 in g.objects(b, TIME.hasEnd):
                                for b_end in g.objects(o4, TIME.inXSDDateTimeStamp):
                                    if a_beg > b_beg and a_end == b_end and a_beg < a_end and b_beg < b_end:
                                        return Literal(True)

    return Literal(False)
