# Context shim (see meta.json): subset of fhirtordf/rdfsupport/fhirgraphutils.py,
# fhirtordf/rdfsupport/namespaces.py and fhirtordf/rdfsupport/dottednamespace.py
# from BD2KOnFHIR/fhirtordf@05b23ba1df9f322c148b7f20ebbd6d58cb92cefc (verified
# against the fhirtordf 1.3.3 PyPI release, same file layout), so the region
# executes outside the package and outside its rdflib~=5.0 pin (this study
# pins rdflib 7.2.1). Identical bindings for both representations.
from typing import Optional, Union
from datetime import datetime, date

from rdflib import Namespace, BNode, Literal, URIRef
from rdflib.term import Node
from rdflib.exceptions import UniquenessError


# fhirtordf/rdfsupport/dottednamespace.py, unmodified: FHIR RDF spells
# properties with a literal dot in the local name (fhir:Coding.system), which
# this namespace produces through attribute chaining.
class DottedNamespace(Namespace):
    """An RDF namespace that supports the FHIR dotted notation (e.g. fhir:Patient.status)."""

    def __new__(cls, value):
        return Namespace.__new__(cls, value)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + item)


class DottedURIRef(URIRef):
    """A URIRef that supports the FHIR dotted notation."""

    def __new__(cls, value, base=None):
        return URIRef.__new__(cls, value, base)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + '.' + item)


# fhirtordf/rdfsupport/namespaces.py, unmodified (this region only needs FHIR).
FHIR = DottedNamespace("http://hl7.org/fhir/")


# fhirtordf/rdfsupport/fhirgraphutils.py, unmodified: the two names the
# extracted region calls but does not define itself.
def value(g, subject: Node, predicate: URIRef, asLiteral=False) -> \
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


class CodeableConcept:
    def __init__(self, system: str, code_: str, uri: Optional[URIRef] = None):
        self.system = system
        self.code = code_
        self.uri = uri

    def __lt__(self, other):
        return repr(self) < repr(other)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        return "({}, {}, {})".format(self.system, self.code, self.uri)

    def __str__(self):
        return 'CodeableConcept("{}", "{}", {})'.format(self.system, self.code,
                                                        'URIRef("{}")'.format(self.uri) if self.uri else "None")
