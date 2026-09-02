# Context shim (see meta.json): subset of fhirtordf/rdfsupport/dottednamespace.py
# and fhirtordf/rdfsupport/namespaces.py plus the `value` helper from
# fhirtordf/rdfsupport/fhirgraphutils.py, all from BD2KOnFHIR/fhirtordf@05b23ba1df,
# reproduced here so the region executes outside the (unpublished) fhirtordf
# package. Identical bindings for both representations.
from typing import Union

from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.exceptions import UniquenessError
from rdflib.term import Node, Literal


class DottedNamespace(Namespace):
    """An RDF namespace that supports the FHIR dotted notation (fhir:Patient.status)."""

    def __new__(cls, value):
        return Namespace.__new__(cls, value)

    def __getattribute__(self, item: str) -> "DottedURIRef":
        if item == "index":
            return DottedURIRef(str(self) + item)
        else:
            return super().__getattribute__(item)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + item)


class DottedURIRef(URIRef):
    def __new__(cls, value, base=None):
        return URIRef.__new__(cls, value, base)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + "." + item)

    def __eq__(self, other):
        if isinstance(self, URIRef) and isinstance(other, URIRef):
            return str(self) == str(other)
        else:
            return False

    def __hash__(self):
        return super().__hash__()


FHIR = DottedNamespace("http://hl7.org/fhir/")


def value(g: Graph, subject: Node, predicate: URIRef, asLiteral=False):
    values = list(set(g.objects(subject, predicate)))
    if len(values) == 0:
        return None

    if all(isinstance(v, BNode) for v in values) and predicate != FHIR.value:
        vv = [gv for gv in set(g.value(v, FHIR.value) for v in values) if gv is not None]
        if len(vv) == 0:
            return None
        elif len(vv) > 1:
            raise UniquenessError(
                "Non-unique values for {} {} : [{}]".format(subject, predicate, ", ".join(vv))
            )
        return vv[0].toPython() if not asLiteral else vv[0]
    else:
        if len(values) > 1:
            raise UniquenessError(
                "Non-unique values for {} {} : [{}]".format(subject, predicate, ", ".join(values))
            )
        return values[0].toPython() if isinstance(values[0], Literal) and not asLiteral else values[0]
