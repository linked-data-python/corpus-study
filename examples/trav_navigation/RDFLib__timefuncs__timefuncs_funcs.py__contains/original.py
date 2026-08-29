# Extracted from RDFLib/timefuncs@dd3bde8727 : timefuncs/funcs.py
# region: contains (lines 29-134, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import RDF, TIME
from rdflib.paths import ZeroOrMore, OneOrMore

def contains(e, ctx) -> Literal:
    """SPARQL tfun:contains(a, b)

    Returns Literal(true) if a is inside b where 'inside' is determined by all
    of the possibilities for its expression within the Time Ontology in OWL, see
    https://www.w3.org/TR/owl-time/#time:inside. Returns Literal(false) otherwise.

    Note that this function is couched in reverse terms to has_inside() and that this function has no correlating
    predicate in OWL TIME

    Use: isInside(a, b) in a SPARQL query, where a is a time:Instant and b is a time:Interval instance.

    Example:

    SELECT ?a ?b
    WHERE {
        ?a a time:Interval .
        ?b a time:Instant .

        FILTER tfun:isInside(?a, ?b)
    }

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

    if (a, TIME.intervalContains * OneOrMore, b) in g:
        return Literal(True)

    if (b, TIME.intervalDuring * OneOrMore, a) in g:
        return Literal(True)

    for a_beginning in g.objects(a, TIME.hasBeginning):
        for a_end in g.objects(a, TIME.hasEnd):
            for b_beginning in g.objects(b, TIME.hasBeginning):
                for b_end in g.objects(b, TIME.hasEnd):
                    # declared
                    if (a_beginning, TIME.before, b_beginning) in g and (
                        a_end,
                        TIME.after,
                        b_end,
                    ) in g:
                        return Literal(True)
                    if (b_beginning, TIME.after, a_beginning) in g and (
                        a_end,
                        TIME.after,
                        b_end,
                    ) in g:
                        return Literal(True)
                    if (b_beginning, TIME.after, a_beginning) in g and (
                        b_end,
                        TIME.before,
                        a_end,
                    ) in g:
                        return Literal(True)
                    if (a_beginning, TIME.before, b_beginning) in g and (
                        b_end,
                        TIME.before,
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
                                        b_beginning_time > a_beginning_time
                                        and a_end_time > b_end_time
                                    ):
                                        return Literal(True)

    if _path_exists(
        g, a, b, [(TIME.intervalContains, "outbound"), (TIME.intervalDuring, "inbound")]
    ):
        return Literal(True)

    return Literal(False)
