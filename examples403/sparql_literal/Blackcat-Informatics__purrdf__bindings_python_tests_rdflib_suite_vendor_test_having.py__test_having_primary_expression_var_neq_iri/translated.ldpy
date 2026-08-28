# Extracted from Blackcat-Informatics/purrdf@3aa4ba514e : bindings/python/tests/rdflib_suite/vendor/test_having.py
# region: test_having_primary_expression_var_neq_iri (lines 31-35, stratum sparql_literal)
# licence of the source repository: see meta.json
g = Graph()

def test_having_primary_expression_var_neq_iri():
    query = "SELECT ?p " "WHERE { ?s ?p ?o } " "GROUP BY ?p HAVING (?p != <urn:foo> )"
    qres = g.query(query)

    assert len(qres) == 2
