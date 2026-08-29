# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/graph/starlight_graph.py
# region: StarlightGraph.update (lines 1389-1421, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode, Literal

def update(self, update_object, processor='sparql',
          initNs=None, initBindings=None, use_store_provided=True, **kwargs):
    """Execute a SPARQL UPDATE.

    For the native rdf-1.2 backend the update is forwarded to the endpoint
    via HTTP unchanged (see starlight.backends.native.native_update).

    Otherwise, SPARQL 1.2 text is parsed via sparql1_2_to_rdf's real
    grammar (prepare_update_12), then lowered to a plain SPARQL 1.1
    algebra (tt:HASH encoding) and handed to rdflib as an
    already-executable Update object - every shape (triple-term WHERE
    patterns, ground triple terms in INSERT/DELETE DATA, triple terms
    in INSERT/DELETE templates) is handled natively by that lowering,
    no post-processing needed here.
    """
    if self._is_native:
        from starlight.backends.native import native_update
        native_update(self.store, self._backend, update_object)
        return None
    if isinstance(update_object, str):
        from sparql1_2_to_rdf.parse12 import prepare_update_12
        from sparql1_2_to_rdf.lower_rdf11 import update_to_rdf11, rdf11_to_update
        prepared_12 = prepare_update_12(update_object, base=kwargs.get('base'), initNs=initNs)
        rdf_graph, root = update_to_rdf11(prepared_12)
        update_object = rdf11_to_update(rdf_graph, root)
    raw = Graph(store=self.store, identifier=self.identifier)
    for prefix, ns in self.namespaces():
        raw.bind(prefix, ns)
    raw.update(update_object, processor=processor,
               initNs=initNs, initBindings=initBindings,
               use_store_provided=use_store_provided)
    self._build_registry_from_store()
    return None
