# Context shim (see meta.json): what the region imports from
# BD2KOnFHIR/fhirtordf@05b23ba1df (fhirtordf is not installed, and needs
# jsonasobj, rdflib 5 and the FHIR metadata vocabulary) so that it executes
# outside the package. Identical bindings for both representations.
#
#   * DottedNamespace, DottedURIRef and FHIR: verbatim from
#     fhirtordf/rdfsupport/dottednamespace.py and namespaces.py.
#   * loads: jsonasobj.loads reduced to json.loads (the stand-in loader below
#     reads two keys of it).
#   * FHIRGraph: tests/utils/base_test_case.py without loading the metadata
#     vocabulary (fhir.ttl), which the region never reads.
#   * FHIRResource: STAND-IN for fhirtordf/loaders/fhirresourceloader.py. The
#     real loader needs the metadata vocabulary to turn the JSON into RDF, so
#     the graph it would produce is frozen in a Turtle file of this directory
#     (LOADER_OUTPUT), written after the loader's add_val: a list element is
#     a blank node with fhir:index, a primitive a blank node with fhir:value.
#     The driver rebinds LOADER_OUTPUT to run the region against loader
#     outputs that differ.
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

HERE = Path(__file__).resolve().parent
LOADER_OUTPUT = "fixture.ttl"


class DottedNamespace(Namespace):
    """
    An RDF namespace that supports the FHIR dotted notation (e.g. fhir:Patient.status)
    """
    def __new__(cls, value):
        return Namespace.__new__(cls, value)

    def __getattribute__(self, item: str) -> "DottedURIRef":
        if item == 'index':
            return DottedURIRef(str(self) + item)
        else:
            return super().__getattribute__(item)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + item)

    def __eq__(self, other):
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


class DottedURIRef(URIRef):
    """
    A URIRef that supports the FHIR dotted notation
    """
    def __new__(cls, value, base=None):
        return URIRef.__new__(cls, value, base)

    def __getattr__(self, item: str) -> "DottedURIRef":
        return DottedURIRef(str(self) + '.' + item)

    def __eq__(self, other):
        if isinstance(self, URIRef) and isinstance(other, URIRef):
            return str(self) == str(other)
        else:
            return False

    def __hash__(self):
        return super().__hash__()


FHIR = DottedNamespace("http://hl7.org/fhir/")


def loads(s):
    import json
    return json.loads(s)


class FHIRGraph(Graph):
    def __init__(self, do_print=True):
        super().__init__()


class FHIRResource:
    def __init__(self, vocabulary, json_fname, base_uri, data=None):
        self.root = data
        self._base_uri = base_uri + ('/' if base_uri[-1] not in '/#' else '')
        self._resource_uri = URIRef(
            self._base_uri + self.root["resourceType"] + '/' + self.root["id"])
        self._g = Graph().parse(HERE / LOADER_OUTPUT, format="turtle")

    @property
    def graph(self):
        return self._g
