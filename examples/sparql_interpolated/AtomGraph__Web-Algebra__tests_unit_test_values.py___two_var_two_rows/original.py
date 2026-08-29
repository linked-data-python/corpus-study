# Extracted from AtomGraph/Web-Algebra@128e184aa8 : tests/unit/test_values.py
# region: _two_var_two_rows (lines 35-39, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
EX_A = "http://ex/a"
EX_B = "http://ex/b"
EX_P = "http://ex/p"

def _two_var_two_rows():
    g = Graph()
    g.add((URIRef(EX_A), URIRef(EX_P), Literal("v1")))
    g.add((URIRef(EX_B), URIRef(EX_P), Literal("v2")))
    return g.query(f"SELECT ?s ?o WHERE {{ ?s <{EX_P}> ?o }} ORDER BY ?s")
