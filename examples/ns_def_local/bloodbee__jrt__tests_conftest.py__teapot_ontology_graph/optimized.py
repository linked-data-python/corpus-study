# Extracted from bloodbee/jrt@2c5b072bcb : tests/conftest.py
# region: teapot_ontology_graph (lines 28-40, stratum ns_def_local)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, Namespace

@pytest.fixture
def teapot_ontology_graph():
    STUFF = Namespace("http://example.org/stuff#")
    g = Graph()
    g.bind("stuff", STUFF)
    g += [
        (STUFF.TeaPot, RDF.type, OWL.Class),
        (STUFF.TeaPot, RDFS.label, Literal("TeaPot")),
        (STUFF.stuffs, RDF.type, OWL.ObjectProperty),
        (STUFF.stuffs, RDFS.label, Literal("stuffs")),
    ]
    return g


# Harness, identical on both sides: reach the fixture body past its decorator.
def demo():
    fn = getattr(teapot_ontology_graph, "__wrapped__", teapot_ontology_graph)
    return fn()
