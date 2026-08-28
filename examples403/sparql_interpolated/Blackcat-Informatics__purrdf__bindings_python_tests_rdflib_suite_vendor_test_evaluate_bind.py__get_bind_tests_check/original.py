# Extracted from Blackcat-Informatics/purrdf@3aa4ba514e : bindings/python/tests/rdflib_suite/vendor/test_evaluate_bind.py
# region: get_bind_tests.check (lines 16-23, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Variable

def check(expr, var, obj):
    r = g.query(
        """
            prefix : <http://example.org/ns#>
            select * where { ?s ?p ?o . %s } """
        % expr
    )
    assert r.bindings[0][Variable(var)] == obj
