"""Validation driver: Query.get_component_model_classes lists owl:Classes.

The region was extracted out of class Query, so the driver supplies a stub
`self` with the two members the method uses: the class_index set (mutated —
so the stub is compared after the call) and get_component_model_class, which
here delegates to the real get_class() of the vendored query/common.py.
"""
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import OWL, RDFS, SKOS

from supermodel_common import get_class

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


class StubQuery:
    """Stand-in for pyLODE's Query object."""

    def __init__(self):
        self.class_index = set()

    def get_component_model_class(self, iri, graph, ignored_classes):
        return get_class(iri, graph, None, ignored_classes)

    def __eq__(self, other):
        return self.class_index == other.class_index


def three_classes_one_ignored():
    g = Graph()
    for local, label in (("Beta", "Beta"), ("Alpha", "Alpha"),
                         ("Ignored", "Ignored")):
        g.add((EX[local], RDF.type, OWL.Class))
        g.add((EX[local], RDFS.label, Literal(label)))
    g.add((EX.Alpha, RDFS.subClassOf, EX.Beta))
    return ((StubQuery(), g, [EX.Ignored]), {})


def no_classes():
    g = Graph()
    g.add((EX.thing, RDF.type, SKOS.Concept))
    return ((StubQuery(), g, []), {})


VERDICT = run_pair(__file__, entry="get_component_model_classes",
                   calls=[three_classes_one_ignored, no_classes])
