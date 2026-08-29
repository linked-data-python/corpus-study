# Extracted from TDCC-NES/askwol@3534557e8b : src/askwol/shacl_runner.py
# region: _prepare (lines 33-36, stratum bind_initbindings)
# licence of the source repository: see meta.json
import functools
from rdflib.plugins.sparql import prepareQuery

@functools.lru_cache(maxsize=256)
def _prepare(query_text: str, init_ns_items: tuple | None, base: str | None):
    init_ns = dict(init_ns_items) if init_ns_items else None
    return prepareQuery(query_text, initNs=init_ns, base=base)


# Demo harness (identical on both sides, see meta.json): `_prepare` returns a
# prepared-query object with no useful `__eq__`, so comparing its return
# value directly (what run_pair's entry/calls path would otherwise do) would
# report a spurious diff on every run -- two independently constructed
# objects are never `==`, translation correct or not. `demo` makes the
# region's actual, observable behaviour comparable instead: that the SAME
# (query_text, init_ns_items, base) triple is served from the cache on a
# second call (`cached`), and that the prepared query, run against a graph,
# yields the expected rows (`rows`).
def demo(query_text, init_ns_items, base, graph):
    prepared = _prepare(query_text, init_ns_items, base)
    prepared_again = _prepare(query_text, init_ns_items, base)
    cached = prepared_again is prepared
    rows = sorted(tuple(str(v) for v in row) for row in graph.query(prepared))
    return cached, rows
