# Context shim (see meta.json): the real test does `from timefuncs import
# is_inside` (via `sys.path.append(...)` to reach the package root from
# `tests/functions/`), which -- through timefuncs/__init__.py's module-level
# side effect -- registers `tfun:isInside` as a SPARQL extension function via
# `register_custom_function`. `timefuncs` is not installed in the pinned
# study venv (the study venv is pinned; the package is not on PyPI there),
# so this shim transcribes VERBATIM the one piece of
# RDFLib/timefuncs@dd3bde8727 the test actually exercises:
# `timefuncs/funcs.py`'s `is_inside`, and the one `register_custom_function`
# call from `timefuncs/__init__.py` that wires it to `tfun:isInside`. The
# function only imports from `rdflib` and the standard library. Identical
# for both representations (same convention as the test_finishes region
# elsewhere in this stratum).
from rdflib import Literal
from rdflib.namespace import TIME
from rdflib.namespace import Namespace
from rdflib.paths import OneOrMore
from rdflib.plugins.sparql.operators import register_custom_function


def is_inside(e, ctx) -> Literal:
    """SPARQL tfun:isInside(a, b)

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

    if (a, TIME.before | TIME.after, b) in g:
        return Literal(False)

    if (b, TIME.inside, a) in g:
        return Literal(True)

    for b_beginning in g.objects(b, TIME.hasBeginning * OneOrMore):
        for b_end in g.objects(b, TIME.hasEnd * OneOrMore):
            # declared
            if (a, TIME.after, b_beginning) in g and (a, TIME.before, b_end) in g:
                return Literal(True)

            # calculated
            for b_beginning_time in g.objects(
                b_beginning,
                TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate,
            ):
                for b_end_time in g.objects(
                    b_end, TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate
                ):
                    for a_time in g.objects(
                        a, TIME.inXSDDateTimeStamp | TIME.inXSDDateTime | TIME.inXSDDate
                    ):
                        if b_beginning_time < a_time < b_end_time:
                            return Literal(True)

    return Literal(False)


TFUN = Namespace("https://w3id.org/timefuncs/")
register_custom_function(TFUN.isInside, is_inside, raw=True)
