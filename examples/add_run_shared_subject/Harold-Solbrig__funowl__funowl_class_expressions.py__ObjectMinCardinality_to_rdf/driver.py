"""Validation driver for Harold-Solbrig__funowl__funowl_class_expressions.py__ObjectMinCardinality_to_rdf.

to_rdf takes `self` (an ObjectMinCardinality) and a graph `g`, adds triples to
`g` in place and returns the fresh blank node `x` -- so the oracle is `g`'s
isomorphism after the call (rdfeval.harness compares every call argument, and
a Graph argument is compared by isomorphism) plus the returned BNode
(compared by kind only -- rdfeval.harness.normalise maps every BNode to the
same marker, since identifiers differ between runs by construction).

`self` is built ONCE per case and closed over, so both sides receive the SAME
object -- only `g` is fresh per side, which matters because self carries no
`__eq__` of its own (see context_shim.py) and comparing two distinct
instances by identity would report a spurious diff unrelated to the
translation (same reasoning as the sibling region Annotatable_TANN in this
lot's stratum).

Two cases exercise both branches of the stratum's `if self.classExpression:`
-- each branch is its own `+{ ; }` island sharing `x` with the unconditional
lead-in (owl:onProperty), never merged across the if/else since that would
change which triples a given call actually asserts (see meta.json):

  * `qualified`   -- classExpression is set: owl:minQualifiedCardinality and
    owl:onClass are asserted.
  * `unqualified` -- classExpression is None: owl:minCardinality alone.
"""
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD

from context_shim import ObjectMinCardinality

from rdfeval.harness import run_pair

OPE = URIRef("http://example.org/onto#hasPart")
CLS = URIRef("http://example.org/onto#Widget")


def case(min_value, class_rdf):
    self_obj = ObjectMinCardinality(
        OPE, Literal(min_value, datatype=XSD.nonNegativeInteger), class_rdf
    )

    def factory():
        return ((self_obj, Graph()), {})
    return factory


VERDICT = run_pair(
    __file__,
    entry="to_rdf",
    calls=[
        case(2, CLS),   # classExpression set: qualified-cardinality branch
        case(1, None),  # classExpression None: plain-cardinality branch
    ],
)
