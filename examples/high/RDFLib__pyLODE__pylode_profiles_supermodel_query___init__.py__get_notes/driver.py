"""Validation driver: get_notes reads five SKOS note predicates off one IRI.

The fixtures build a small SKOS graph so that every branch of the region is
exercised (all five note kinds, several values for one kind, then an IRI with
no note at all).  The returned list[Note] is compared element by element --
Note is a dataclass from context.py, so both sides use the very same class.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

EX = "http://example.org/"

TTL = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ex:   <http://example.org/> .

ex:Thing skos:note "a plain note"@en ;
    skos:changeNote "changed in v2" ;
    skos:editorialNote "needs review" ;
    skos:historyNote "was called Widget" ;
    skos:scopeNote "applies to widgets only" ;
    skos:prefLabel "Thing" .

ex:Other skos:note "first" , "second" .

ex:Bare skos:prefLabel "Bare" .
"""


def _call(target):
    def fixture():
        g = Graph()
        g.parse(data=TTL, format="turtle")
        return ((URIRef(target), g), {})
    return fixture


VERDICT = run_pair(
    __file__,
    entry="get_notes",
    calls=[
        _call(EX + "Thing"),   # one note of each of the five kinds
        _call(EX + "Other"),   # two values for the same predicate
        _call(EX + "Bare"),    # no notes at all
    ],
)
