"""Validation driver for Query.load_component_model.

The region is a method of pyLODE's ``Query``.  Everything it calls comes
from ``pylode_context`` (the real pyLODE code, see that module), except
``self.get_component_model_classes``, which is a method of ``Query`` whose
own construction would require loading a full profile hierarchy from the
network.  ``Holder`` therefore supplies that one method, returning a fixed
list of real ``pylode`` ``Class`` objects, and records its arguments so the
harness can check both sides drove it identically.

Everything the translation actually changed stays real: ``db.value(iri,
sh:order)`` and the four ``get_rdf_properties(owl:…Property, …)`` calls run
against a real ``Dataset``, and a wrong IRI would show up immediately as a
different ``ComponentModel``.
"""
from rdflib import Dataset, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SDO, SH, SKOS

from rdfeval.harness import run_pair, graphs_isomorphic

from pylode_context import Class, CodedProperty, LODE, Profile, Resource

EX = "https://example.org/"
CM = URIRef(EX + "component-model")


class Holder:
    """Stand-in for the pyLODE Query instance the method is bound to."""

    def __init__(self, classes):
        self._classes = classes
        self.calls = []

    def get_component_model_classes(self, graph, ignored_classes):
        self.calls.append((graph.identifier, sorted(map(str, ignored_classes))))
        return list(self._classes)

    def __eq__(self, other):
        return self.calls == other.calls and self._classes == other._classes

    def __repr__(self):
        return f"Holder(calls={self.calls!r})"


class TripleIterDataset(Dataset):
    """A Dataset that iterates triples instead of quads.

    The harness compares every Graph argument by isomorphism, and
    ``rdflib.compare`` cannot consume the quads a plain Dataset yields.
    Nothing in the region (nor in the pyLODE helpers it calls) iterates the
    dataset directly, so this only affects the comparison.
    """

    def __init__(self):
        # pyLODE's own ProfilesDataset uses default_union=True; without it the
        # region's db-level reads (get_name, db.value, ...) see nothing.
        super().__init__(default_union=True)

    def __iter__(self):
        for s, p, o, _c in super().__iter__():
            yield s, p, o


def _dataset():
    ds = TripleIterDataset()
    g = ds.graph(CM)
    g.add((CM, RDFS.label, Literal("Test component model")))
    g.add((CM, SKOS.definition, Literal("A component model used for testing.")))
    g.add((CM, LODE.ignoreClass, URIRef(EX + "Ignored")))
    g.add((CM, SH.order, Literal(3)))
    g.add((CM, SDO.workExample, URIRef(EX + "example1")))
    g.add((URIRef(EX + "example1"), RDF.type, SDO.TextObject))
    g.add((URIRef(EX + "example1"), SDO.name, Literal("An example")))
    g.add((URIRef(EX + "example1"), SDO.description, Literal("Shows a thing.")))
    g.add((URIRef(EX + "example1"), SDO.encodingFormat, Literal("text/turtle")))
    g.add((URIRef(EX + "example1"), DCTERMS.source, Literal("hand written")))
    g.add((URIRef(EX + "example1"), SH.order, Literal(1)))
    g.add((URIRef(EX + "example1"), SDO.text, Literal("<a> <b> <c> .")))

    for local, prop_type in (("note", OWL.AnnotationProperty),
                             ("count", OWL.DatatypeProperty),
                             ("relatedTo", OWL.ObjectProperty),
                             ("imports", OWL.OntologyProperty)):
        iri = URIRef(EX + local)
        g.add((iri, RDF.type, prop_type))
        g.add((iri, RDFS.label, Literal(local)))
        g.add((iri, SKOS.definition, Literal(f"The {local} property.")))
    # OWL 2 subclass of owl:ObjectProperty: picked up by the object-property
    # branch of get_rdf_properties only
    g.add((URIRef(EX + "sameHeightAs"), RDF.type, OWL.SymmetricProperty))
    g.add((URIRef(EX + "sameHeightAs"), RDFS.label, Literal("sameHeightAs")))
    return ds


def case_plain_classes():
    parent = Class(URIRef(EX + "Parent"), "Parent")
    child = Class(URIRef(EX + "Child"), "Child", superclasses=[parent])
    return ((Holder([parent, child]), CM, _dataset()), {})


def case_coded_properties():
    profile = Profile(URIRef(EX + "profile"), "Profile")
    coded = CodedProperty(
        URIRef(EX + "colour"), "colour", "The colour.", profile,
        codelist=[Resource(URIRef(EX + "colours"), "colours")])
    uncoded = CodedProperty(
        URIRef(EX + "shape"), "shape", "The shape.", profile)
    cls = Class(URIRef(EX + "Thing"), "Thing",
                properties={"prop": [coded, coded, uncoded]})
    return ((Holder([cls]), CM, _dataset()), {})


def case_no_classes():
    return ((Holder([]), CM, _dataset()), {})


VERDICT = run_pair(__file__, entry="load_component_model",
                   calls=[case_plain_classes, case_coded_properties,
                          case_no_classes])
