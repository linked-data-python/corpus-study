# Extracted from AtomGraph/Web-Algebra@128e184aa8 : tests/unit/test_values.py
# region: _bnode_value (lines 58-61, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
EX_A = "http://ex/a"
EX_P = "http://ex/p"

def _bnode_value():
    g = Graph()
    g.add((URIRef(EX_A), URIRef(EX_P), BNode("b1")))
    return g.query(f"SELECT ?o WHERE {{ <{EX_A}> <{EX_P}> ?o }}")
