"""Validation driver for
sebneu__portalwatch__converter_portal_fetch_processors.py__CKANDCAT_fetchAndConvertToDCAT.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side and is what `graph`
already holds before the call -- but the traversal pattern this region reads
(hydra pagination, then dcat:Dataset subjects) does not live in the graph it
is handed: it lives in what `graph.parse(portal_api, ...)` and the pagination
loop *fetch*.  `fetchAndConvertToDCAT` never touches the network here: the
"fetch" is `graph.parse()` given a local file path, which rdflib treats like
any other input source, so `portal_api` and `hydra:nextPage` in this driver's
extra fixtures (fixture_ckan_page1.ttl, fixture_ckan_page2.ttl,
fixture_ckan_page1_nopagination.ttl -- see design record corpus/403) point at
files on disk instead of URLs.

_parse_atom-style multi-argument signature (self, graph, portal_ref,
portal_api, snapshot, activity, format="ttl") means the single-argument call
`fixture=` alone would build does not fit, hence `calls=`:

  * with_pagination -- portal_api is fixture_ckan_page1.ttl, whose
    hydra:nextPage hops once to fixture_ckan_page2.ttl before terminating
    (page2 has no further nextPage). Exercises all three m{ }.first() sites
    with a match each, and the final loop with two dcat:Dataset solutions.
  * no_pagination -- portal_api is fixture_ckan_page1_nopagination.ttl, a
    hydra:PagedCollection with no hydra:nextPage triple at all: the
    zero-solution case for the second m{ }.first() (the one that decides
    whether the while loop runs at all), and for the final loop too (no
    dcat:Dataset subject).

`self` is unused by the region (never read through it), so `None` stands in.
`portal_ref` / `snapshot` / `activity` are opaque to the region -- `activity`
only reaches quality.add_quality_measures, which context_shim/quality.py
stubs as a no-op (see its header) -- so plain placeholder strings stand in.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent


def _call(page1_name):
    # `graph` (from fixture.ttl) is parsed fresh per side, as usual. The
    # other arguments carry no state the region mutates, so building them
    # once and sharing them between both sides (rather than rebuilding
    # inside `make`) is just simpler here -- unlike the shared graph
    # fixture, there is no comparison hazard either way since they are
    # already-equal strings/None.
    portal_api = str(HERE / page1_name)

    def make():
        graph = fixture_graph("fixture.ttl")
        return (
            (None, graph, "test-portal", portal_api, "test-snapshot", "test-activity"),
            {},
        )
    return make


VERDICT = run_pair(
    __file__,
    entry='fetchAndConvertToDCAT',
    fixture="fixture.ttl",
    calls=[
        _call("fixture_ckan_page1.ttl"),
        _call("fixture_ckan_page1_nopagination.ttl"),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. The
    # region returns None; what is actually compared is the final state of
    # `graph` (isomorphism, since it is an rdflib.Graph -- see
    # rdfeval.harness._compare_value) and the other, order-irrelevant
    # arguments.
)
