"""Validation driver for city-knowledge-graphs__python__lab7_OWLReasoning.py__checkEntailment.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdflib import Graph
from rdfeval.harness import run_pair


def _make_case(triple: str):
    def _case():
        g = Graph()
        g.parse(data="""
            @prefix ex: <http://example.org/> .
            ex:s1 ex:p1 ex:o1 .
            ex:s2 ex:p2 ex:o2 .
        """, format="turtle")
        return (g, triple), {}
    return _case


VERDICT = run_pair(
    __file__,
    entry='checkEntailment',
    calls=[
        # a triple pattern that holds
        _make_case("<http://example.org/s1> <http://example.org/p1> <http://example.org/o1>"),
        # a triple pattern that does not hold
        _make_case("<http://example.org/s1> <http://example.org/p1> <http://example.org/nope>"),
    ],
)
