"""Validation driver for mariocosenza__kgsum__src_dataset_preparation.py__select_local_license.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.  `select_local_license(parsed_graph)` takes a single
graph argument and always finds *something or nothing* in it (no second
parameter to vary), so the zero-solution case needs a second graph with no
`dcterms:license` triple at all -- `calls=` supplies both explicitly instead
of relying on the single-call default `fixture=` alone would build.

Further calls (repair): the repository only ever passes a `rdflib.Graph`
(`_guess_format_and_parse` returns one or raises), but the region wraps the
query in a `try`, so the `except` branch is exercised too.  An argument that
is not a graph (`None`, a `str`, an arbitrary object) must make BOTH versions log
the SPARQL error and return `set()`: the `s{ }` query is lazy, so only a
translation that forces it inside the `try` keeps that.  A graph whose
`triples` raises stands for an error during the evaluation, which escapes the
`try` on both sides (rdflib iterates lazily as well) and must raise the same
exception type and message.  A graph with a single, falsy license (`""`) and
one carrying a blank node and a typed literal check that `str(row.license)`
is applied to whatever term the graph holds, and that a falsy string is kept.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _empty_graph():
    g = Graph()
    g.parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        ex:dataset4 dcterms:title "No license here" .
    """, format="turtle")
    return g


class _NotAGraph:
    """An arbitrary object; two instances compare equal so the harness, which
    also compares the arguments after the call, does not report a difference
    between the two fresh instances."""

    def __eq__(self, other):
        return type(other) is type(self)

    __hash__ = object.__hash__


class _BrokenGraph(Graph):
    """A graph whose evaluation raises once the query reads its triples."""

    def triples(self, triple):
        if triple[1] is None:  # the harness's own whole-graph iteration
            return super().triples(triple)
        raise ValueError("store unavailable")


def _falsy_license_graph():
    g = Graph()
    g.parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        ex:dataset5 dcterms:license "" .
        ex:dataset5 dcterms:rights "all rights reserved" .
    """, format="turtle")
    return g


def _typed_license_graph():
    g = Graph()
    g.parse(data="""
        @prefix dcterms: <http://purl.org/dc/terms/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        [] dcterms:license "0"^^xsd:integer .
    """, format="turtle")
    return g


VERDICT = run_pair(
    __file__,
    entry='select_local_license',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(FIXTURE),), {}),  # several solutions, plus neighbourhood
        lambda: ((_empty_graph(),), {}),           # zero-solution case
        lambda: ((_falsy_license_graph(),), {}),   # a single license "" is kept
        lambda: ((_typed_license_graph(),), {}),   # blank-node subject, typed literal
        lambda: ((None,), {}),                     # not a graph: except -> set()
        lambda: (("not a graph",), {}),            # a str, same
        lambda: ((_NotAGraph(),), {}),             # an arbitrary object, same
        lambda: ((_BrokenGraph(),), {}),           # error while evaluating: same raise
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
