"""Validation driver for tgbugs__pyontutils__pyontutils_core.py__makeGraph_replace_uriref.

The region rewrites a graph in place: for every triple in which `find` is the
subject, the predicate or the object, it adds the triple with `replace` in that
position (through `makeGraph.add_trip`, which coerces CURIEs and drops an empty
object) and removes the original, fully bound.  It returns nothing; the oracle
is the state of the `makeGraph` it was called on, graph by isomorphism and
prefix bindings by name, from the same input on both sides.

The context is the class the method hangs on (pyontutils_context.py): the
`check_thing` / `add_trip` of the repository, copied, and a graph handed in.

Calls (a fresh graph from fixture.ttl each time, one makeGraph per call):

  1. `find` and `replace` are IRIs: every position is rewritten, including the
     triples with ex:old twice or three times, which pass through half-replaced
     states (the region's own warning), and the neighbours (ex:oldish, another
     namespace's `old`) stay.
  2. `find` and `replace` are CURIEs ('ex:old', 'ex:new'): `check_thing`
     expands the first, `add_trip` the second, in every position.
  3. `find` matches nothing (zero solutions): the graph is unchanged.
  4. `replace` is an empty literal: `add_trip` refuses an empty OBJECT, so the
     triples where `find` was an object are removed and not replaced, while the
     ones where it was a subject or predicate are replaced.  A translation that
     removed only when the add happened would differ.
  5. `find` is a literal, matched in the object position only.
  6. `replace` is a CURIE with an unknown prefix: `add_trip` raises KeyError at
     the first triple, with the graph untouched on that triple; the raise and
     the partial state are compared.
"""
from pathlib import Path

from rdflib import Literal, Namespace, URIRef

from pyontutils_context import makeGraph
from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
EX = Namespace("http://example.org/")


def call(find, replace):
    def make():
        mg = makeGraph(fixture_graph(FIXTURE), {"ex": EX})
        return ((mg, find, replace), {})
    return make


VERDICT = run_pair(
    __file__,
    entry="replace_uriref",
    fixture="fixture.ttl",
    calls=[
        call(EX.old, EX.new),
        call("ex:old", "ex:new"),
        call(EX.nothing, EX.new),
        call(EX.old, Literal("")),
        call(Literal("a literal object"), EX.new),
        call(EX.old, "unknown:new"),
    ],
)
