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

    g.add((STUFF.TeaPot, RDF.type, OWL.Class))
    g.add((STUFF.TeaPot, RDFS.label, Literal("TeaPot")))

    g.add((STUFF.stuffs, RDF.type, OWL.ObjectProperty))
    g.add((STUFF.stuffs, RDFS.label, Literal("stuffs")))

    return g
