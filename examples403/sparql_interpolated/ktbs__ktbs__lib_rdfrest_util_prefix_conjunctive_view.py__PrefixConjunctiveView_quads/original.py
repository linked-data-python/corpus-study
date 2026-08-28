# Extracted from ktbs/ktbs@4f9f50c770 : lib/rdfrest/util/prefix_conjunctive_view.py
# region: PrefixConjunctiveView.quads (lines 223-253, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import ConjunctiveGraph, Graph, Literal, Variable
_FAIL = "Graph is not included in this PrefixConjunctiveView"

def quads(self, triple_or_quad=None):
    """Iterate over all the quads in the entire conjunctive graph"""

    s,p,o,c = self._spoc(triple_or_quad)
    if c is _FAIL:
        return

    initBindings = {}
    graph_cache = {}
    store = self.store
    if s is not None:
        initBindings['s'] = s
    if p is not None:
        initBindings['p'] = p
    if o is not None:
        initBindings['o'] = o
    if c is not None:
        initBindings['g'] = c
        graph_cache[c] = Graph(store, c, self)
        filter_clause = ""
    else:
        filter_clause = self._filter

    for s, p, o, g in self._whole.query('SELECT ?s ?p ?o ?g'
                                        '{ GRAPH ?g { ?s ?p ?o } %s}'
                                        % filter_clause,
                                        initBindings=initBindings):
        ctx = graph_cache.get(g)
        if ctx is None:
            ctx = graph_cache[g] = Graph(store, g, self)
        yield s, p, o, ctx
