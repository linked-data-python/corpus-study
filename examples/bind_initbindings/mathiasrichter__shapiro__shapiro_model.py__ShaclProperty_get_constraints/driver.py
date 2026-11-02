"""Validation driver for ShaclProperty.get_constraints.

The region reads a graph through three initBindings queries (the property and
its super-properties; their SHACL constraints; the members of an sh:in list)
and returns a sorted list of ShaclConstraint. Oracle: the values both
versions produce from the same fixture, ordered (the region sorts).

`self` is a ShaclProperty of shim.py built per side on a fresh fixture graph.

Calls:

* PS1   own constraints (minCount, datatype, an sh:in enumeration read back
        as a list of literals) PLUS maxLength inherited from ex:generalName
        through sh:path/rdfs:subPropertyOf; the storage order of the
        constraints is not the sorted order, and ex:comment is not an SHACL
        constraint;
* PS2   no SHACL constraint: empty list;
* PS3   exactly one constraint;
* PS4   its own constraints; PS1's and unrelatedSuper's must not leak in;
* bn1   a blank-node shape (added by hand: Turtle renames its bnodes) with
        an sh:in enumeration: the BNode branch of `prop`;
* bn2   a blank-node shape whose path leads to ex:enumSub, whose
        super-property carries sh:in: the constraint's subject is an IRI
        while self.iri is a blank node, so the enumeration is looked up on
        URIRef("bn2") and found empty.
"""
from pathlib import Path

from rdflib import BNode, Literal, Namespace
from rdflib.collection import Collection

from rdfeval.harness import fixture_graph, run_pair
from shim import ShaclProperty

FIXTURE = Path(__file__).parent / "fixture.ttl"
EX = Namespace("http://example.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")


def _graph():
    g = fixture_graph(FIXTURE)
    bn1, head = BNode("bn1"), BNode("bn1list")
    g.add((bn1, SH.path, EX.colour))
    g.add((bn1, SH.maxCount, Literal(2)))
    Collection(g, head, [Literal("S"), Literal("M"), Literal("L")])
    g.add((bn1, SH["in"], head))
    bn2 = BNode("bn2")
    g.add((bn2, SH.path, EX.enumSub))
    g.add((bn2, SH.minCount, Literal(1)))
    return g


def _case(iri):
    def make():
        return (ShaclProperty(iri, _graph()),), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="get_constraints",
    calls=[_case(str(EX[n])) for n in ("PS1", "PS2", "PS3", "PS4")]
          + [_case("bn1"), _case("bn2")],
    ordered=True,  # the region sorts by constraint IRI
)
