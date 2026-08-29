# Extracted from Blackcat-Informatics/purrdf@3aa4ba514e : bindings/python/tests/rdflib_suite/vendor/test_agg_distinct.py
# region: test_count_distinct (lines 71-119, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef

def test_count_distinct():
    g = Graph()

    g.parse(
        format="turtle",
        publicID="http://example.org/",
        data="""
    @prefix : <> .

    <#a>
      :knows <#b>, <#c> ;
      :age 42 .

    <#b>
      :knows <#a>, <#c> ;
      :age 36 .

    <#c>
      :knows <#b>, <#c> ;
      :age 20 .

    """,
    )

    # Query 1: people knowing someone younger
    results = g.query(
        """
    PREFIX : <http://example.org/>

    SELECT DISTINCT ?x {
      ?x :age ?ax ; :knows [ :age ?ay ].
      FILTER( ?ax > ?ay )
    }
    """
    )
    assert len(results) == 2

    # nQuery 2: count people knowing someone younger
    results = g.query(
        """
    PREFIX : <http://example.org/>

    SELECT (COUNT(DISTINCT ?x) as ?cx) {
      ?x :age ?ax ; :knows [ :age ?ay ].
      FILTER( ?ax > ?ay )
    }
    """
    )
    assert list(results)[0][0].toPython() == 2
