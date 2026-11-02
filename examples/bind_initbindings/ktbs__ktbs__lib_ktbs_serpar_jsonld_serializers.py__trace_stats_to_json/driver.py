"""Validation driver for ktbs trace_stats_to_json.

The region reads a graph (two queries on the statistics of ONE trace, bound
by initBindings) and returns the statistics as a dict. Oracle: the values
both versions produce from the same fixture.

Calls (fixture.ttl parsed afresh per side):

* t1: simple statistics (only the predicates of the stats namespace, ex:label
      and rdf:type are filtered out), a time span, and three obselCountPerType
      blank nodes grouped by node: the sort by ?bn is what makes the groups
      contiguous;
* t2: statistics but no obselCountPerType and no minTime;
* t3: a trace with no statistics at all;
* t4: another trace's statistics, which t1 must not see (and the reverse).

The blank nodes of the two sides have different identifiers, hence
ordered=False (the order of the groups follows the identifiers).
"""
from pathlib import Path
from types import SimpleNamespace

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"


def _case(trace):
    def make():
        uri = URIRef("http://example.org/" + trace + "/")
        tstats = SimpleNamespace(
            uri=URIRef("http://example.org/" + trace + "/@stats"),
            trace=SimpleNamespace(uri=uri, model_uri="http://example.org/model"))
        return (fixture_graph(FIXTURE), tstats), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="trace_stats_to_json",
    calls=[_case(t) for t in ("t1", "t2", "t3", "t4")],
    ordered=False,
)
