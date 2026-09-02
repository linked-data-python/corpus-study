# Context shim (see meta.json): `value()` from BD2KOnFHIR/fhirtordf@05b23ba1df
# fhirtordf/rdfsupport/fhirgraphutils.py, lines 11-28 -- the function `code()`
# (this region) calls but does not define. Copied verbatim so the region
# executes outside the package. Identical bindings for both representations.
from typing import Union
from datetime import date, datetime
from rdflib import Graph, BNode, Literal
from rdflib.term import URIRef, Node
from rdflib.exceptions import UniquenessError
from fhirtordf.rdfsupport.namespaces import FHIR


def value(g: Graph, subject: Node, predicate: URIRef, asLiteral=False) -> \
        Union[None, BNode, URIRef, str, date, bool, datetime, int, float]:

    values = list(set(g.objects(subject, predicate)))
    if len(values) == 0:
        return None

    if all(isinstance(v, BNode) for v in values) and predicate != FHIR.value:
        vv = [gv for gv in set(g.value(v, FHIR.value) for v in values) if gv is not None]
        if len(vv) == 0:
            return None
        elif len(vv) > 1:
            raise UniquenessError("Non-unique values for {} {} : [{}]".format(subject, predicate, ', '.join(vv)))
        return vv[0].toPython() if not asLiteral else vv[0]
    else:
        if len(values) > 1:
            raise UniquenessError("Non-unique values for {} {} : [{}]".format(subject, predicate, ', '.join(values)))
        return values[0].toPython() if isinstance(values[0], Literal) and not asLiteral else values[0]
