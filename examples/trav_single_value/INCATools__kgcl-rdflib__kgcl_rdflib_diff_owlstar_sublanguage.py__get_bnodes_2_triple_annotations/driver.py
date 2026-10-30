"""Validation driver for INCATools__kgcl-rdflib__kgcl_rdflib_diff_owlstar_sublanguage.py__get_bnodes_2_triple_annotations.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each input below is parsed fresh for each side.

`entry='demo'`, not `get_bnodes_2_triple_annotations` itself (see
original.py): the region returns a dict KEYED BY BNODE, and rdflib mints a
fresh internal id for every blank node on every parse -- run_pair calls the
fixture-loading callable once per side, so the two sides' graphs (and every
BNode in them) are never identity-comparable. `demo` repackages the result
into a sorted, bnode-identity-free structure first.  It keeps the subject,
the predicate and the object of every collected triple (the subject relative
to the dict key, "self"), so the `s` -> `i` rewrite of the inner scan is
observed, not assumed.

The calls, in order, and what each one exercises:

  fixture.ttl      the shipped input: two complete annotations with extra
                   triples (one has a BNode object, filtered out), a partial
                   one (absent from the intersection), a NAMED subject (in the
                   intersection, skipped by isinstance), two decoys missing
                   one or two of the three predicates
  empty            no triple at all: {} on both sides
  multi-ab         annotatedSource/Property/Target each with TWO values,
                   written a-then-b: next() takes the first the store yields,
                   .first() must take the same one (demo shows which)
  multi-ba         the same, written b-then-a
  extras-first     the extra triples are written BEFORE the three owl:annotated*
                   ones, so a `.first()` read whose predicate were widened to
                   a variable would return the extra triple's object
  bnode-values     three annotations, each with ONE of source / property /
                   target a blank node: the isinstance guards then drop every
                   extra triple of that annotation (the extras stay visible on
                   a fourth, plain, annotation)
  falsy            source "" , property 0, target false, extras "" and 0: no
                   truth test may stand in for presence

The zero-solution case of the three single-value reads (next() raises
StopIteration, .first() gives None) is unreachable: the loop only visits
nodes of source & property & target, built from the same three predicates
(see meta.json).
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent

_PRE = """\
@prefix ex:  <http://example.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
"""

INPUTS = {
    "empty": "",
    "multi-ab": _PRE + """
_:m owl:annotatedSource ex:SrcA , ex:SrcB ;
    owl:annotatedProperty ex:propA , ex:propB ;
    owl:annotatedTarget ex:TgtA , ex:TgtB ;
    ex:comment "kept" .
""",
    "multi-ba": _PRE + """
_:m owl:annotatedSource ex:SrcB , ex:SrcA ;
    owl:annotatedProperty ex:propB , ex:propA ;
    owl:annotatedTarget ex:TgtB , ex:TgtA ;
    ex:comment "kept" .
""",
    "extras-first": _PRE + """
_:x ex:comment "first in store order" ;
    ex:weight 7 ;
    owl:annotatedSource ex:Alice ;
    owl:annotatedProperty ex:knows ;
    owl:annotatedTarget ex:Bob .
_:y ex:note "another annotation" ;
    owl:annotatedSource ex:Carol ;
    owl:annotatedProperty ex:likes ;
    owl:annotatedTarget ex:Dave .
""",
    "bnode-values": _PRE + """
_:bs owl:annotatedSource [ ex:n 1 ] ;
     owl:annotatedProperty ex:knows ;
     owl:annotatedTarget ex:Bob ;
     ex:comment "dropped: source is a bnode" .
_:bp owl:annotatedSource ex:Alice ;
     owl:annotatedProperty [ ex:n 2 ] ;
     owl:annotatedTarget ex:Bob ;
     ex:comment "dropped: property is a bnode" .
_:bt owl:annotatedSource ex:Alice ;
     owl:annotatedProperty ex:knows ;
     owl:annotatedTarget [ ex:n 3 ] ;
     ex:comment "dropped: target is a bnode" .
_:ok owl:annotatedSource ex:Alice ;
     owl:annotatedProperty ex:knows ;
     owl:annotatedTarget ex:Carol ;
     ex:comment "kept" .
""",
    "falsy": _PRE + """
_:f owl:annotatedSource "" ;
    owl:annotatedProperty 0 ;
    owl:annotatedTarget false ;
    ex:comment "" ;
    ex:weight 0 .
""",
}


def _parsed(text):
    return lambda: ((Graph().parse(data=text, format="turtle"),), {})


VERDICT = run_pair(
    __file__,
    entry='demo',
    fixture="fixture.ttl",
    calls=[lambda: ((fixture_graph(HERE / "fixture.ttl"),), {})]
    + [_parsed(text) for text in INPUTS.values()],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. demo's
    # own output is already a canonical sorted list either way.
)
