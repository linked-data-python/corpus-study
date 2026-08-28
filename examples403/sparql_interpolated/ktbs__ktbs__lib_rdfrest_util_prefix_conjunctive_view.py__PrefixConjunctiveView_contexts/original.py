# Extracted from ktbs/ktbs@4f9f50c770 : lib/rdfrest/util/prefix_conjunctive_view.py
# region: PrefixConjunctiveView.contexts (lines 145-165, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import ConjunctiveGraph, Graph, Literal, Variable

def contexts(self, triple=None):
    """Iterate over all contexts in the graph

    If triple is specified, iterate over all contexts the triple is in.
    """
    #initBindings = {}
    if triple:
        ## the right thing to do would be
        # initBindings['s'], initBindings['p'], initBindings['o'] = triple
        ## but this would not work with Virtuoso,
        ## so we have to hangle both case differently
        inner_where = "%s %s %s" % tuple(i.n3() for i in triple)
    else:
        inner_where = "?s ?p ?o"
    store = self.store
    for gid, in self._whole.query('SELECT DISTINCT ?g'
                                  '{GRAPH ?g { %s } %s}'
                                  % (inner_where, self._filter),
                                  #initBindings=initBindings,
                                  ):
        yield Graph(store, gid, self)
