# Extracted from tgbugs/pyontutils@cb3efcd10f : pyontutils/combinators.py
# region: Restriction.parse (lines 405-427, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from pyontutils.closed_namespaces import rdf, rdfs, owl

def parse(self, *triples, root=None, graph=None):  # drop, parse, contract
    if graph is None:
        graph = rdflib.Graph()
        [graph.add(t) for t in triples]

    self.triples = []
    for r_s in graph.subjects(rdf.type, owl.Restriction):
        local_trips = [(r_s, rdf.type, owl.Restriction)]
        try:
            s = next(graph.subjects(self.predicate, r_s))  # FIXME cases where there is more than one???
            t = s, self.predicate, r_s
            local_trips.append(t)
            p = next(graph.objects(r_s, owl.onProperty))
            t = r_s, owl.onProperty, p
            local_trips.append(t)
            o = next(graph.objects(r_s, self.scope))
            t = r_s, self.scope, o
            local_trips.append(t)
        except StopIteration:
            print(f'failed to parse {r_s} {self.predicate} {self.scope} {local_trips}')
            continue
        self.triples.extend(local_trips)
        yield self.RestrictionTriple((s, p, o))  # , self.__class__.__name__
