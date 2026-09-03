# Context shim (see meta.json): fhirtordf/rdfsupport/fhirgraphutils.py from
# BD2KOnFHIR/fhirtordf@05b23ba1df, trimmed to the ONE function this region
# imports and calls (`value`), verbatim. `value` is a module-level helper
# defined elsewhere in the real fhirgraphutils.py -- it is NOT part of the
# extracted region (test_value only calls it) -- so it is left as plain
# rdflib code and imported identically by both original.py and
# translated.ldpy, the same convention as `_term_label` in
# mapsa__blathers__src_blathers_extract.py___extract_nested_node.
from typing import Union, Optional, Tuple, List

from rdflib import Graph, BNode, Literal, RDF
from rdflib.term import Identifier, URIRef, Node
from rdflib.exceptions import UniquenessError

from fhirtordf.rdfsupport.namespaces import FHIR


def value(g: Graph, subject: Node, predicate: URIRef, asLiteral=False):
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
