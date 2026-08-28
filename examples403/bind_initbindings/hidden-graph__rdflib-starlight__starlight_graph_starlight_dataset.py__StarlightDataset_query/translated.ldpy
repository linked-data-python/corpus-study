# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/graph/starlight_dataset.py
# region: StarlightDataset.query (lines 459-513, stratum bind_initbindings)
# licence of the source repository: see meta.json
from starlight.graph.starlight_graph import (
    StarlightGraph, VALID_BACKENDS, _raw_triples, _read_source_text,
)
from starlight.model.encoding import TT_NS, ENCODING_PREDS as _ENCODING_PREDS, lookup_tt_hash, restore_select_bindings

def query(self, query_object, processor='sparql', result='sparql',
          initNs=None, initBindings=None, use_store_provided=True, **kwargs):
    """Execute a SPARQL query across all named graphs with SPARQL-star support.

    SPARQL 1.2 syntax (``<<( )>>``, ``{| |}``, ``~``, SUBJECT/PREDICATE/
    OBJECT/isTRIPLE) is parsed via sparql1_2_to_rdf's real grammar and
    lowered to plain SPARQL 1.1 (tt:HASH encoding) before execution.
    SELECT result rows are post-processed to restore tt:HASH URIRefs
    back to TripleTerm objects.

    Rewriting and parsing are cached (``prepare_query_cached``) on
    (query text, effective namespaces, base) - not cleared on
    parse()/update() unlike ``_raw_execution_graph``, since a query's
    parse tree depends only on its own text, not on graph content.

    For the native rdf-1.2 backend the query is routed through
    ``starlight.backends.native.native_query``, same as
    ``StarlightGraph.query()`` (a native-backed dataset's contexts all
    share one store, so it's the same underlying HTTP operation) -
    ``_build_raw_execution_graph()``'s plain-Graph-copy approach can't
    represent real triple-term-valued bindings (rdflib's SPARQL JSON
    result parsing doesn't understand "type":"triple"; see
    starlight.backends.native's module docstring).
    """
    if self._backend == 'rdf-1.2':
        from starlight.backends.native import native_query
        return native_query(
            self.store, self._backend, query_object, processor=processor, result=result,
            initNs=initNs, initBindings=initBindings,
            use_store_provided=use_store_provided, **kwargs,
        )

    if isinstance(query_object, str):
        # No remote-store dispatch complexity needed here unlike
        # StarlightGraph: _build_raw_execution_graph() below is
        # *always* a fresh, local, in-memory Dataset copy (no store=
        # argument) regardless of what this dataset's own backing
        # store is, so the resulting Query object can always be handed
        # to it directly.
        from starlight.query.query_cache import prepare_query_cached
        effective_ns = initNs if initNs else dict(self.namespaces())
        query_object = prepare_query_cached(
            self._prepared_query_cache, query_object, effective_ns, kwargs.get('base')
        )
    raw = self._build_raw_execution_graph()
    r = raw.query(query_object, processor=processor, result=result,
                  initNs=initNs, initBindings=initBindings,
                  use_store_provided=use_store_provided, **kwargs)
    if r.type == 'SELECT':
        restore_select_bindings(r, self._restore_any)
    elif r.type == 'CONSTRUCT':
        from starlight.model.encoding import inject_missing_tt_encoding
        inject_missing_tt_encoding(r.graph, self._restore_any)
        r.graph = StarlightGraph.from_rdflib(r.graph)
    return r
