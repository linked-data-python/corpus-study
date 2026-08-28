"""Validation driver: Query.get_summary_vocabularies builds the vocab table.

The region was extracted out of class Query, so the driver supplies a stub
`self` with the two members it reads: `db` (a Dataset whose named graphs hold
the qb:CodedProperty declarations) and `component_models` (the in-memory
model objects that carry the classes each coded property belongs to).
"""
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, QB, RDF, RDFS, SKOS

from supermodel_model import (Class, CodedProperty, ComponentModel, Profile,
                              ProfileType)

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


class StubQuery:
    """Stand-in for pyLODE's Query object (read-only here)."""

    def __init__(self, db, component_models):
        self.db = db
        self.component_models = component_models

    def __eq__(self, other):
        return True  # not mutated by the region; the return value is compared


def _dataset():
    db = Dataset()
    g = Graph(identifier=URIRef("http://example.org/graph/1"))
    g.add((EX.colour, RDF.type, QB.CodedProperty))
    g.add((EX.colour, RDFS.label, Literal("Colour")))
    g.add((EX.colour, SKOS.definition, Literal("The colour of the thing.")))
    g.add((EX.colour, QB.codeList, EX.colours))
    g.add((EX.colours, RDFS.label, Literal("Colour scheme")))
    g.add((EX.size, RDF.type, QB.CodedProperty))
    g.add((EX.size, RDFS.label, Literal("Size")))
    g.add((EX.size, QB.codeList, EX.sizes))
    g.add((EX.sizes, RDFS.label, Literal("Size scheme")))
    for s, p, o in g:
        db.add((s, p, o, g))
    return db


def _component_models():
    profile = Profile(EX.profile, "Test profile", ProfileType.ROOT)
    klass = Class(EX.Thing, "Thing")
    coded = CodedProperty(EX.colour, "Colour", "The colour of the thing.",
                          profile, belongs_to_class=klass)
    klass.properties = {"Property": [coded]}
    return [ComponentModel(EX.cm, "Component model", {}, classes=[klass])]


def populated():
    return ((StubQuery(_dataset(), _component_models()),), {})


def empty_dataset():
    return ((StubQuery(Dataset(), []),), {})


VERDICT = run_pair(__file__, entry="get_summary_vocabularies",
                   calls=[populated, empty_dataset])
