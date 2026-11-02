"""Validation driver for MaximeJakubowski__sls_project__slsparser_shapels.py___target_parse.

`_target_parse(graph, shapename)` builds a shape-algebra tree from the target
declarations of a shape; its one existence read is
`(shapename, rdf:type, rdfs:Class) in graph` (a shape that is also an
rdfs:Class is an implicit class target).  The tree is an `SANode` whose
`__eq__` compares the operator and the children recursively, so a missing or
extra COUNTRANGE child, or a different operator, is a difference.

The fixture is read fresh for each side.  Calls:
  ShapeAll        -> OR of 2 targetNode + 2 targetClass + the implicit class
                     target (existence TRUE) + subjectsOf + objectsOf
  ShapeClassOnly  -> existence TRUE alone: a single child, returned as is
  ShapeNodeOnly   -> existence FALSE, one child, returned as is
  ShapeNone       -> existence FALSE, nothing at all: Op.BOT
  OwlClassShape, SubclassShape, MentionShape, SwapShape: neighbours that
  must not match -> Op.BOT (ex:OtherClass IS an rdfs:Class, so every
  "existence FALSE" call above also has a class node elsewhere in the graph)
  the blank-node shape (an rdfs:Class, found through its ex:marker): a BNode
  interpolated in subject position -> a single targetClass child plus the
  implicit one -> OR of 2
  an IRI absent from the graph -> Op.BOT
"""
from rdflib import Literal, Namespace

from rdfeval.harness import run_pair, fixture_graph
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


def _case(shape):
    return lambda: ((lambda g: (g, shape))(fixture_graph(FIXTURE)), {})


def _anon():
    g = fixture_graph(FIXTURE)
    return (g, g.value(None, EX.marker, Literal("anon"))), {}


VERDICT = run_pair(
    __file__,
    entry='_target_parse',
    calls=[
        _case(EX.ShapeAll),
        _case(EX.ShapeClassOnly),
        _case(EX.ShapeNodeOnly),
        _case(EX.ShapeNone),
        _case(EX.OwlClassShape),
        _case(EX.SubclassShape),
        _case(EX.MentionShape),
        _case(EX.SwapShape),
        _case(EX.NotInTheGraph),
        _anon,
    ],
)
