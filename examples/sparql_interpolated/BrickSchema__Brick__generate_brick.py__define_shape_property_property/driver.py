"""Validation driver for BrickSchema__Brick__generate_brick.py__define_shape_property_property.

This region READS a graph (the `optional and no other keys` branch queries
the current graph for an existing, unconstrained sh:PropertyShape) and also
WRITES to it, so the oracle is the equality of the graph mutated by each
side from the same input graph (design record corpus/405), plus whatever the
call returns.  `fixture.ttl` is parsed fresh for each side.

The entry point does not take a lone graph argument — its signature is
`define_shape_property_property(shape_name, definitions, graph=...)` — so
`calls=` supplies shape_name/definitions explicitly and passes the freshly
parsed fixture as the `graph` keyword; `run_pair` compares that kwarg after
the call (graph isomorphism) exactly as it would a positional `graph=`
argument taken from `fixture=`.

`definitions` is exercised across every branch the region has:
  - "or": a nested recursive definition (sh:or + rdf:Collection)
  - optional + no other key, existing shape found -> reuse (read via s{ })
  - optional + no other key, existing shape NOT found -> create new
  - datatype (plain) -> sh:datatype
  - datatype == BSH.NumericValue -> sh:or bsh:NumericValue
  - values -> sh:in + rdf:Collection
`definitions` is mutated in place (.pop) by the region, so the call is a
fresh callable invoked once per side.
"""
from pathlib import Path

from rdflib import URIRef, Literal
from rdflib.namespace import Namespace

from rdfeval.harness import run_pair, fixture_graph

EX = Namespace("http://example.org/")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

_FIXTURE = Path(__file__).parent / "fixture.ttl"


def _make_call():
    def build():
        graph = fixture_graph(_FIXTURE)
        definitions = {
            "or": [
                {EX.hasSubArea: {"datatype": XSD.string}},
            ],
            EX.hasWindow: {"optional": True},
            EX.hasTag: {"optional": True},
            EX.hasColor: {"datatype": XSD.string},
            EX.hasWeight: {"datatype": BSH.NumericValue},
            EX.hasStatus: {"values": ["open", "closed"]},
        }
        return (EX.MainShape, definitions), {"graph": graph}
    return build


VERDICT = run_pair(
    __file__,
    entry="define_shape_property_property",
    calls=[_make_call()],
    # No store promises an order among the SPARQL rows the region's read
    # branch matches; the fixture is built so the branch it drives never has
    # to pick among several (see fixture.ttl), so ordered=True is safe and
    # this is not a `fixture=` run in the harness's single-argument sense.
    ordered=True,
)
