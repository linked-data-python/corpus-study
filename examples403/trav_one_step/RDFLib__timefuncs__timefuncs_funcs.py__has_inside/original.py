# Extracted from RDFLib/timefuncs@dd3bde8727 : timefuncs/funcs.py
# region: has_inside (lines 231-292, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import RDF, TIME
from rdflib.paths import ZeroOrMore, OneOrMore

def has_inside(e, ctx) -> Literal:
    """SPARQL tfun:hasInside(a, b)

    Returns Literal(true) if a has b inside it where 'inside' is determined by all
    of the possibilities for its expression within the Time Ontology in OWL, see
    https://www.w3.org/TR/owl-time/#time:inside. Returns Literal(false) otherwise.

    Note that this function is couched in reverse terms to is_inside() and that is_inside() has no correlating
    predicate in OWL TIME

    Use: hasInside(a, b) in a SPARQL query, where a is a time:Interval and b is a time:Instant instance.

    Example:

    SELECT ?a ?b
    WHERE {
        ?a a time:Interval .
        ?b a time:Instant .

        FILTER tfun:hasInside(?a, ?b)
    }

    """
    try:
        a = e.expr[0]
        b = e.expr[1]
    except Exception as err:
        raise ValueError(
            "This function, hasInside(a, b), requires two IRI parameters, "
            "where a & b are Time Ontology Interval and Instant instances, respectively. "
            "a is tested to have b inside it"
        )

    g = ctx.ctx.graph

    if (a, TIME.before | TIME.after, b) in g:
        return Literal(False)

    if (a, TIME.inside, b) in g:
        return Literal(True)

    for a_beginning in g.objects(a, TIME.hasBeginning * OneOrMore):
        for a_end in g.objects(a, TIME.hasEnd * OneOrMore):
            # declared
            if (b, TIME.after, a_beginning) in g and (b, TIME.before, a_end) in g:
                return Literal(True)

            # calculated
            for a_beginning_time in g.objects(
                a_beginning,
                TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate,
            ):
                for a_end_time in g.objects(
                    a_end, TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate
                ):
                    for b_time in g.objects(
                        b, TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate
                    ):
                        if a_beginning_time < b_time < a_end_time:
                            return Literal(True)

    return Literal(False)
