# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/ktbs_root.py
# region: KtbsRoot.get_state (lines 90-138, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import ConjunctiveGraph, Graph, RDF, RDFS
from ..namespace import KTBS
from ..utils import SKOS

def get_state(self, parameters=None):
    """I override `~rdfrest.cores.ICore.get_state`:meth:

    I support parameter "prop" to enrich the KtbsRoot description with additional information.
    I consider an empty dict as equivalent to no dict.
    """
    state = super(KtbsRoot, self).get_state(parameters)
    if not parameters:
        return state

    enriched_state = Graph()
    enriched_state += state
    whole = ConjunctiveGraph(self.service.store)
    initNs = { '': KTBS, 'rdfs': RDFS, 'skos': SKOS }
    initBindings = { 'base': self.uri }
    for prop in parameters['prop']:
        if prop == 'comment':
            enriched_state.addN(
                (s, RDFS.comment, o, enriched_state)
                for s, o, _ in whole.query('''
                    SELECT ?s ?o
                      $root # selected solely to please Virtuoso
                    {
                        GRAPH $root { $root :hasBase ?s }
                        GRAPH ?s    { ?s rdfs:comment ?o }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'label':
            enriched_state.addN(
                (s, p, o, enriched_state)
                for s, p, o, _ in whole.query('''
                    SELECT ?s ?p ?o
                      $root # selected solely to please Virtuoso
                    {
                        VALUES ?p { rdfs:label skos:prefLabel }
                        GRAPH $root { $root :hasBase ?s }
                        GRAPH ?s    {
                            $root :hasBase ?s.
                            ?s ?p ?o.
                        }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        else:
            pass # ignoring unrecognized properties
            # should we signal them instead (diagnosis?)

    return enriched_state
