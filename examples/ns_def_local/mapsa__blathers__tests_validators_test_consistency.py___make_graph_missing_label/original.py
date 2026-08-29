# Extracted from mapsa/blathers@cad7822217 : tests/validators/test_consistency.py
# region: _make_graph_missing_label (lines 50-56, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

def _make_graph_missing_label() -> Graph:
    """Graph with a class missing rdfs:label."""
    g = Graph()
    EX = Namespace("http://example.org/test#")
    g.bind("ex", EX)
    g.add((EX.NoLabel, RDF.type, OWL.Class))
    return g
