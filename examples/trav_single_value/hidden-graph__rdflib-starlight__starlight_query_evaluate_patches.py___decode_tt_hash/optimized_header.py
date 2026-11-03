# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/query/evaluate_patches.py
# region: _decode_tt_hash (lines 670-708, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF, URIRef

def _decode_tt_hash(graph, node):
    """Decode `node` (a tt:HASH URIRef) into its raw (subject, predicate,
    object) encoding triples, read directly from `graph`. Returns None for
    anything that isn't a tt:HASH URIRef with encoding triples present in
    `graph`.

    Deliberately *not* recursive - `subject`/`object` are returned exactly
    as read (which may themselves be a nested tt:HASH URIRef, or may not),
    never pre-decoded into a tuple here. `_tt_aware_eq` is what recurses,
    by calling this function again on each component it compares - keeping
    every value this function ever returns a single, consistent shape (an
    rdflib term, never a tuple) is what makes that recursion correct;
    pre-decoding a nested component here produced a tuple one level too
    early, which `_tt_aware_eq`'s own recursive call then couldn't
    re-decode (`isinstance(node, URIRef)` is false for a tuple), silently
    falling through to `a.eq(b)` on two raw tuples and crashing - confirmed
    a real bug this way, not a hypothetical, via the W3C `op-2` fixture's
    own nested-triple-term case.

    Deliberately reads the *graph's own* rdf:subject/predicate/object
    triples rather than a `StarlightGraph._tt_nodes` Python-side registry:
    the graph object seen during query evaluation (`ctx.graph`) is a bare
    `rdflib.Graph` view over the same store (see
    `StarlightGraph.query()` - `raw = Graph(store=self.store, ...)`), not
    the `StarlightGraph` instance itself, so `_tt_nodes` isn't reachable
    from here. Reading the on-store encoding triples directly works
    identically to (and is the same technique as) `StarlightGraph.
    _build_registry_from_store()`'s own reconstruction.
    """
    from shim_encoding import TT_NS  # see meta.json: context shim

    if not (isinstance(node, URIRef) and str(node).startswith(TT_NS)):
        return None
    triple = tuple(graph.value(node, predicate)
                   for predicate in (RDF.subject, RDF.predicate, RDF.object))
    return None if None in triple else triple
