# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/base.py
# region: Base.get_state (lines 39-136, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import ConjunctiveGraph, Graph, RDF, RDFS
from ..namespace import KTBS, KTBS_NS_URI
from ..utils import SKOS

def get_state(self, parameters=None):
    """I override `~rdfrest.cores.ICore.get_state`:meth:

    I support parameter "prop" to enrich the Base description with additional information.
    I consider an empty dict as equivalent to no dict.
    """
    state = super(Base, self).get_state(parameters)
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
                      $base # selected solely to please Virtuoso
                    {
                        GRAPH $base { $base :contains ?s }
                        GRAPH ?s    { ?s rdfs:comment ?o }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'hasMethod':
            enriched_state.addN(
                (s, KTBS.hasMethod, o, enriched_state)
                for s, o, _ in whole.query('''
                    SELECT ?t ?m
                        $base # selected solely to please Virtuoso
                    {
                        GRAPH $base { $base :contains ?t }
                        GRAPH ?t    { ?t :hasMethod ?m }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'hasModel':
            enriched_state.addN(
                (s, KTBS.hasModel, o, enriched_state)
                for s, o, _ in whole.query('''
                    SELECT ?t ?m
                      $base # selected solely to please Virtuoso
                    {
                        GRAPH $base { $base :contains ?t }
                        GRAPH ?t    { ?t :hasModel ?m }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'hasSource':
            enriched_state.addN(
                (s, KTBS.hasSource, o, enriched_state)
                for s, o, _ in whole.query('''
                    SELECT ?t1 ?t2
                      $base # selected solely to please Virtuoso
                    {
                        GRAPH $base { $base :contains ?t1 }
                        GRAPH ?t1   { ?t1 :hasSource ?t2 }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'label':
            enriched_state.addN(
                (s, p, o, enriched_state)
                for s, p, o, _ in whole.query('''
                    SELECT ?s ?p ?o
                      $base # selected solely to please Virtuoso
                    {
                        VALUES ?p { rdfs:label skos:prefLabel }
                        GRAPH $base { $base :contains ?s }
                        GRAPH ?s    {
                            $base :contains ?s.
                            ?s ?p ?o.
                        }
                    }
                ''', initNs=initNs, initBindings=initBindings)
            )
        elif prop == 'obselCount':
            enriched_state.addN(
                (s, KTBS.hasObselCount, o, enriched_state)
                for s, o, _ in whole.query('''
                    SELECT ?t (COUNT(?obs) as ?c)
                        (SAMPLE($base) as ?sample_base) # selected solely to please Virtuoso
                    {
                        VALUES ?tt { :StoredTrace :ComputedTrace }
                        GRAPH $base { $base :contains ?t. ?t a ?tt }
                        OPTIONAL { ?obs :hasTrace ?t }
                    } GROUP BY ?t
                ''', initNs=initNs, initBindings=initBindings)
            )
        else:
            pass # ignoring unrecognized properties
            # should we signal them instead (diagnosis?)

    return enriched_state
