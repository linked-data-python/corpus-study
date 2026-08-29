# Extracted from Blackcat-Informatics/purrdf@3aa4ba514e : bindings/python/tests/rdflib_suite/vendor/test_agg_distinct.py
# region: test_sum_distinct (lines 30-42, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
query_tpl = """
SELECT ?x (MIN(?y_) as ?y) (%s(DISTINCT ?z_) as ?z) {
  VALUES (?x ?y_ ?z_) {
    ("x1" 10 1)
    ("x1" 11 1)
    ("x2" 20 2)
  }
} GROUP BY ?x ORDER BY ?x
"""

def test_sum_distinct():
    g = Graph()
    results = g.query(query_tpl % "SUM")
    results = [[lit.toPython() for lit in line] for line in results]

    # this is the tricky part
    assert results[0][2] == 1, results[0][2]

    # still check the whole result, to be on the safe side
    assert results == [
        ["x1", 10, 1],
        ["x2", 20, 2],
    ], results
