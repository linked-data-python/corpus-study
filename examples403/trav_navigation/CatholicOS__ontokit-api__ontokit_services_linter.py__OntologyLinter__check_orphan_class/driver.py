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

Two calls: the fixture graph (three orphan classes exercising every arm of
the "excluding owl:Thing" logic, plus neighbours that fail on a parent, on a
child, on the blank-node guard, and on not being typed owl:Class at all --
see fixture.ttl), and an empty graph for the zero-solution case.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph
from context_shim import OntologyLinter

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
_RECEIVER = OntologyLinter()


def _case(graph_factory):
    return lambda: ((_RECEIVER, graph_factory()), {})


VERDICT = run_pair(
    __file__,
    entry="run_check_orphan_class",
    fixture="fixture.ttl",
    calls=[
        _case(lambda: fixture_graph(FIXTURE)),
        _case(Graph),
    ],
)
