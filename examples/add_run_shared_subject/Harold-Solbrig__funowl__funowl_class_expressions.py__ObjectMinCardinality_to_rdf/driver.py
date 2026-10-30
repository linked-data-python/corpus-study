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

Repair of 2026-10-30 (triage: equivalence-doubt) -- the sub-terms of the
first two cases return a constant and write nothing, whereas funowl's real
ones write into `g`, and the island evaluates every interpolation before it
writes (record ldpy/014).  The stand-ins below mirror the real to_rdf of
funowl@69e1cbe2f6 and RECORD each visit in `g` itself (`drv:log drv:stepN
"name"`, N = how many visits came before): the log is part of the compared
graph, so the order and the number of sub-to_rdf calls are compared too.
They read only their own log triples, as the real ones read only what they
wrote (rdflib Collection) or the namespace bindings (AbbreviatedIRI).

  * `structured qualified` -- ObjectInverseOf as the property (writes
    `_:i owl:inverseOf <p>`, objectproperty_expressions.py:25),
    ObjectIntersectionOf as the class (writes `_:c a owl:Class ;
    owl:intersectionOf ( ... )` through SEQ, class_expressions.py:86) and a
    minimum of 0 (the falsy NonNegativeInteger, general_definitions.py:39):
    nested blank nodes compared by isomorphism, call order visible.
  * `structured unqualified` -- same property, no class, into a graph that
    already holds another restriction: what the region adds next to it.
  * `raising min_` -- min_.to_rdf raises in the unqualified branch: same
    exception (type and message) and the same partial graph on both sides
    (type + onProperty written by the first island, nothing by the second).
    A raise in objectPropertyExpression.to_rdf or classExpression.to_rdf
    WOULD leave a different partial graph (ldpy/014); funowl only reaches it
    on an undeclared prefix (AbbreviatedIRI.to_rdf, general_definitions.py:
    141) and no caller keeps the graph after the exception (cli.py:42-43
    discards it, no test catches it), so it is not a case here.
"""
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, XSD

from context_shim import ObjectMinCardinality

from rdfeval.harness import run_pair

OPE = URIRef("http://example.org/onto#hasPart")
CLS = URIRef("http://example.org/onto#Widget")
EX = Namespace("http://example.org/onto#")
DRV = Namespace("http://example.org/driver#")


def _visit(g, name):
    """Record one sub-to_rdf call in `g`, numbered by the calls before it."""
    n = len(list(g.triples((DRV.log, None, None))))
    g.add((DRV.log, DRV[f"step{n}"], Literal(name)))


class Leaf:
    """ObjectProperty / Class (an IRI) or NonNegativeInteger: a fixed term."""

    def __init__(self, name, term, error=None):
        self.name, self.term, self.error = name, term, error

    def to_rdf(self, g, emit_type_arc=False):
        _visit(g, self.name)
        if self.error is not None:
            raise self.error
        return self.term


class InverseOf:
    """funowl ObjectInverseOf.to_rdf: `_:x owl:inverseOf T(P)`."""

    def __init__(self, prop):
        self.prop = prop

    def to_rdf(self, g, emit_type_arc=False):
        _visit(g, "ObjectInverseOf")
        x = BNode()
        g.add((x, OWL.inverseOf, self.prop.to_rdf(g)))
        return x


class IntersectionOf:
    """funowl ObjectIntersectionOf.to_rdf, with SEQ (rdf_converter.py:10)."""

    def __init__(self, *members):
        self.members = list(members)

    def to_rdf(self, g, emit_type_arc=False):
        _visit(g, "ObjectIntersectionOf")
        subj = BNode()
        g.add((subj, RDF.type, OWL.Class))
        seq = BNode()
        Collection(g, seq, [m.to_rdf(g) for m in self.members])
        g.add((subj, OWL.intersectionOf, seq))
        return subj


def case(min_value, class_rdf):
    self_obj = ObjectMinCardinality(
        OPE, Literal(min_value, datatype=XSD.nonNegativeInteger), class_rdf
    )

    def factory():
        return ((self_obj, Graph()), {})
    return factory


def structured(ope, min_, ce, seed=False):
    """`self` with the given sub-terms; `seed` pre-fills g with another
    restriction, so the case also shows what the region leaves beside it."""
    self_obj = ObjectMinCardinality(None, None)
    self_obj.objectPropertyExpression, self_obj.min_ = ope, min_
    self_obj.classExpression = ce

    def factory():
        g = Graph()
        if seed:
            r = BNode()
            g.add((r, RDF.type, OWL.Restriction))
            g.add((r, OWL.onProperty, EX.other))
            g.add((r, OWL.minCardinality,
                   Literal(3, datatype=XSD.nonNegativeInteger)))
        return ((self_obj, g), {})
    return factory


def nni(n):
    return Leaf(f"min {n}", Literal(n, datatype=XSD.nonNegativeInteger))


VERDICT = run_pair(
    __file__,
    entry="to_rdf",
    calls=[
        case(2, CLS),   # classExpression set: qualified-cardinality branch
        case(1, None),  # classExpression None: plain-cardinality branch
        # nested blank nodes written by the sub-terms, min 0, call order
        structured(InverseOf(Leaf("hasPart", OPE)), nni(0),
                   IntersectionOf(Leaf("Widget", CLS), Leaf("Gadget", EX.Gadget))),
        # unqualified, next to an existing restriction
        structured(InverseOf(Leaf("hasPart", OPE)), nni(5), None, seed=True),
        # min_.to_rdf raises in the unqualified branch
        structured(Leaf("hasPart", OPE),
                   Leaf("min", None, ValueError("bad cardinality")), None),
    ],
)
