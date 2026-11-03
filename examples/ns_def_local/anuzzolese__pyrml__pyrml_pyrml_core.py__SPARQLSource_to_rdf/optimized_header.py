# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: SPARQLSource.to_rdf (lines 1976-1989, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF

def to_rdf(self):
    sd = Namespace('http://www.w3.org/ns/sparql-service-description#')

    g = Graph().add((self, RDF.type, sd.Service))

    if self.endpoint:
        g.add((self, sd.endpoint, self.endpoint))

    if self.result_format:
        g.add((self, sd.resultFormat, self.result_format))

    return g
