"""Validation driver for TestSparqlFunctions._query (rdflib-starlight).

`_query(self, g, expr)` splices `expr` -- a SPARQL expression handed in by the
caller -- into `SELECT ?s (<expr> AS ?v) WHERE { ?s ex:title ?t }` and returns
{subject: value}.  `self` is unused.  The calls vary the expression so that the
projected value shows which pattern and which text were sent:

  * `?t` itself, `STR(?t)`, `LANG(?t)`, `UCASE(?t)`, `STRLEN(?t)`;
  * a constant, `42`, to show every title subject gets a row (and ex:e, whose
    predicate is ex:label, and ex:f do not);
  * `LANGMATCHES(LANG(?t), "en")`, which is a boolean per title;
  * an expression that is not SPARQL (`(((`): the parse error is the outcome,
    compared by type and message;
  * the empty graph: an empty dict.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(expr, empty=False):
    def _make():
        g = Graph() if empty else fixture_graph(FIXTURE)
        return (None, g, expr), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='_query',
    calls=[
        call("?t"),
        call("STR(?t)"),
        call("LANG(?t)"),
        call("UCASE(?t)"),
        call("STRLEN(?t)"),
        call("42"),
        call('LANGMATCHES(LANG(?t), "en")'),
        call("((("),
        call("?t", empty=True),
    ],
)
