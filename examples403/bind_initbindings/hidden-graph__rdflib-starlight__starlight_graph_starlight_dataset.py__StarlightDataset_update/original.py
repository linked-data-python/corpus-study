# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/graph/starlight_dataset.py
# region: StarlightDataset.update (lines 515-568, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, URIRef, BNode

def update(self, update_object, processor='sparql',
           initNs=None, initBindings=None, use_store_provided=True, **kwargs):
    """Execute a SPARQL UPDATE across named graphs with SPARQL-star support.

    Triple-term patterns in WHERE clauses are rewritten to SPARQL 1.1
    (rdf-1.1 backend only — see below). All cached per-graph registries
    are rebuilt after execution so that newly added triple terms are
    immediately visible.

    Remote-store (Fuseki/Oxigraph) updates bypass rdflib's own
    ``Dataset(store=...).update()`` and are sent over HTTP directly (see
    ``starlight.backends.native.native_update``) — needed for *both*
    backends: rdflib's ``SPARQLStore._is_contextual()`` treats any string
    graph identifier other than the literal ``"__UNION__"`` as needing a
    wrapping ``GRAPH { }`` block, and doesn't special-case ``Dataset``'s
    own ``DATASET_DEFAULT_GRAPH_ID`` sentinel (a ``URIRef``, which
    subclasses ``str``) - so ``Dataset.update()`` always wrapped the
    *entire* update text in an extra ``GRAPH <urn:x-rdflib:default> { }``
    block, which nests illegally around any update that already has its
    own ``GRAPH <uri> { }`` clause (the normal way to target a named graph
    from dataset-level SPARQL). Confirmed via real Oxigraph and Fuseki
    testing: a plain ``INSERT DATA { GRAPH <uri> {...} }`` with no triple
    terms at all got a 400 from both. For the rdf-1.2 backend the update
    text is sent unmodified (the endpoint understands ``<<( )>>``
    natively); for rdf-1.1 it is parsed and lowered to the tt:HASH
    encoding first (native_update itself, via sparql1_2_to_rdf).
    """
    is_remote_http_store = bool(
        getattr(self.store, 'query_endpoint', None) and getattr(self.store, 'update_endpoint', None)
    )
    if not is_remote_http_store:
        if isinstance(update_object, str):
            from sparql1_2_to_rdf.parse12 import prepare_update_12
            from sparql1_2_to_rdf.lower_rdf11 import update_to_rdf11, rdf11_to_update
            prepared_12 = prepare_update_12(update_object, base=kwargs.get('base'), initNs=initNs)
            rdf_graph, root = update_to_rdf11(prepared_12)
            update_object = rdf11_to_update(rdf_graph, root)
        # default_union forwarded from self - same rationale as
        # _build_raw_execution_graph(): a GRAPH-less WHERE clause should
        # see the same default-graph-is-the-union semantics self.triples()
        # honors, not silently match against an empty default graph.
        raw = Dataset(store=self.store, default_union=self.default_union)
        for prefix, ns in self.namespaces():
            raw.bind(prefix, ns)
        raw.update(update_object, processor=processor,
                   initNs=initNs, initBindings=initBindings,
                   use_store_provided=use_store_provided, **kwargs)
    else:
        from starlight.backends.native import native_update
        native_update(self.store, self._backend, update_object)
    for sg in self._sg_cache.values():
        sg._build_registry_from_store()
    self._raw_execution_graph = None
    return None
