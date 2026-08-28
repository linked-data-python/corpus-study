# Extracted from RDFLib/timefuncs@dd3bde8727 : tests/test_is_before_standalone.py
# region: test_is_before_rdflib (lines 165-183, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, BNode
g = Graph().parse(str(tests_dir / "data" / "before.ttl"))

def test_is_before_rdflib():
    BEFORE = Namespace("https://w3id.org/timefuncs/testdata/before/")

    assert is_before_rdflib(g, BEFORE.a01, BEFORE.b01)
    assert is_before_rdflib(g, BEFORE.a02, BEFORE.b02)
    assert is_before_rdflib(g, BEFORE.a03, BEFORE.b03)
    assert is_before_rdflib(g, BEFORE.a04, BEFORE.b04)
    assert is_before_rdflib(g, BEFORE.a05, BEFORE.b05)
    assert is_before_rdflib(g, BEFORE.a06, BEFORE.b06)
    assert is_before_rdflib(g, BEFORE.a08, BEFORE.b08)
    assert is_before_rdflib(g, BEFORE.a09, BEFORE.b09)
    assert is_before_rdflib(g, BEFORE.a10, BEFORE.b10)
    assert is_before_rdflib(g, BEFORE.a11, BEFORE.b11)

    assert not is_before_rdflib(g, BEFORE.a01, BEFORE.b02)
    assert not is_before_rdflib(g, BEFORE.foo, BEFORE.bar)
    assert not is_before_rdflib(g, BEFORE.b01, BEFORE.a01)
    assert not is_before_rdflib(g, BEFORE.b07, BEFORE.a07)
    assert not is_before_rdflib(g, BEFORE.b10, BEFORE.a10)
