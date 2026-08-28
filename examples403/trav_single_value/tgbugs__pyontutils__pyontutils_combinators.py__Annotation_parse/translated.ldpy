# Extracted from tgbugs/pyontutils@cb3efcd10f : pyontutils/combinators.py
# region: Annotation.parse (lines 594-609, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from pyontutils.closed_namespaces import rdf, rdfs, owl

def parse(self, *triples, graph=None):
    if graph is None:  # TODO decorator for this
        graph = rdflib.Graph()
        [graph.add(t) for t in triples]

    rspt = rdf.type, owl.annotatedSource, owl.annotatedProperty, owl.annotatedTarget
    for a_s in graph.subjects(rdf.type, owl.Axiom):
        s_s = next(graph.objects(a_s, owl.annotatedSource))
        s_p = next(graph.objects(a_s, owl.annotatedProperty))
        s_o = next(graph.objects(a_s, owl.annotatedTarget))
        triple = s_s, s_p, s_o

        # TODO combinator? or not in this case?
        yield triple, tuple((a_p, a_o)
                            for a_p, a_o in graph.predicate_objects(a_s)
                            if a_p not in rspt)
