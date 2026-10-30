"""Validation driver for CatholicOS__ontokit-api__ontokit_services_linter.py__OntologyLinter__check_orphan_class.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_check_orphan_class` is `async def` in its home class (no `await` inside the
region's own 40 lines) and a method (`self, graph`); `run_check_orphan_class`
(see original.py) drives the coroutine to completion, since `run_pair` calls
its entry point synchronously with no event loop. `self` only needs the two
static helpers `_get_local_name`/`_get_label` -- see context_shim.py. A
single, stateless `_RECEIVER` instance is reused for every call on both
sides: a fresh instance per side would fail the harness's default `==`
(object identity) for a reason unrelated to translation correctness.

Three calls:

* the fixture graph: orphan classes exercising every arm of the "excluding
  owl:Thing" logic, plus neighbours that fail on a parent, on a child, on
  the blank-node guard, and on not being typed owl:Class at all.  The repair
  of 2026-10-30 added one neighbour per mutant the first fixture left green
  (see fixture.ttl, last section): another predicate pointing at an orphan
  (children island widened to `?s ?r {class_uri}`), a blank-node parent
  (`isinstance(p, URIRef)` guard removed), untyped URIRef and blank-node
  children (children restricted to typed classes), and owl:Class as the
  object of another predicate (candidate island widened to `?r`);
* fixture_thing.ttl: owl:Thing typed owl:Class with neither parent nor
  child, so that only the `class_uri == owl_thing` skip keeps it out of the
  result -- in fixture.ttl it has a child and the skip is unobservable;
* an empty graph for the zero-solution case.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph
from context_shim import OntologyLinter

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
FIXTURE_THING = HERE / "fixture_thing.ttl"
_RECEIVER = OntologyLinter()


def _case(graph_factory):
    return lambda: ((_RECEIVER, graph_factory()), {})


VERDICT = run_pair(
    __file__,
    entry="run_check_orphan_class",
    fixture="fixture.ttl",
    calls=[
        _case(lambda: fixture_graph(FIXTURE)),
        _case(lambda: fixture_graph(FIXTURE_THING)),
        _case(Graph),
    ],
)
