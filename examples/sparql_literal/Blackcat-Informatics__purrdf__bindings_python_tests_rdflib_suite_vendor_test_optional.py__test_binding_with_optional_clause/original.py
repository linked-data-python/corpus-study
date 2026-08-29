# Extracted from Blackcat-Informatics/purrdf@3aa4ba514e : bindings/python/tests/rdflib_suite/vendor/test_optional.py
# region: test_binding_with_optional_clause (lines 4-37, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Variable

def test_binding_with_optional_clause() -> None:
    """
    Optional clauses should bind variables if feasible.

    See https://github.com/RDFLib/rdflib/issues/2957
    """
    g = Graph().parse(
        data="""
        prefix ex:  <https://www.example.org/>
        ex:document ex:subject "Nice cars" .
        ex:someCar   ex:type "Car" .
        """
    )
    result = g.query(
        """prefix ex:  <https://www.example.org/>
        select ?subject ?car
        where  {
                $this ex:subject ?subject.
                optional
                {
                 # an offending subselect clause
                 select ?car
                 where {
                           ?car ex:type "Car".
                       }
                  }
            }"""
    )
    assert len(result.bindings) == 1
    (first,) = result.bindings
    assert first.get(Variable("car")) == URIRef("https://www.example.org/someCar")
    assert first.get(Variable("subject")) == Literal(
        "Nice cars"
    ), "optional clause didnt bind"
