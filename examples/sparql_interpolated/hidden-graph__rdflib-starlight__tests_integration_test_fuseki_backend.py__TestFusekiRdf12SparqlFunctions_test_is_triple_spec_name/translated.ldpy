# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/integration/test_fuseki_backend.py
# region: TestFusekiRdf12SparqlFunctions.test_is_triple_spec_name (lines 367-371, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import URIRef, Literal
EX        = 'http://example.org/'

def test_is_triple_spec_name(self, sg_rdf12):
    r = sg_rdf12.query(f"""
        SELECT (isTRIPLE(TRIPLE(<{EX}a>, <{EX}b>, <{EX}c>)) AS ?v) WHERE {{}}
    """)
    assert r.bindings[0][r.vars[0]] == Literal(True)
