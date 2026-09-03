"""Validation driver for CatholicOS__ontokit-api__ontokit_services_linter.py__OntologyLinter__check_undefined_parent.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_check_undefined_parent` is `async def` in its home class (no `await`
inside the region's own 40 lines) and a method (`self, graph`);
`run_check_undefined_parent` (see original.py) drives the coroutine to
completion, since `run_pair` calls its entry point synchronously with no
event loop. `self` only needs the two static helpers
`_get_local_name`/`_get_label` -- see context_shim.py. A single, stateless
`_RECEIVER` instance is reused for every call on both sides: a fresh
instance per side would fail the harness's default `==` (object identity)
for a reason unrelated to translation correctness.

Two calls: the fixture graph (two undefined-parent violations, one of them
with an rdfs:label exercising `_get_label`'s non-None branch, plus
neighbours that must NOT match -- owl:Thing as parent, a defined parent, a
class with no parent at all, a non-owl:Class subject, a blank-node class, a
blank-node parent and a literal parent -- see fixture.ttl), and an empty
graph for the zero-solution case.
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
    entry="run_check_undefined_parent",
    fixture="fixture.ttl",
    calls=[
        _case(lambda: fixture_graph(FIXTURE)),
        _case(Graph),
    ],
)
