# Extracted from surroundaustralia/cheka@31505e6804 : cheka/cheka.py
# region: Cheka._expand_profiles_graph (lines 134-146, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import DCTERMS, PROF, RDF, SH

def _expand_profiles_graph(self, pg: Graph):
    # type all profiles
    # dcterms:Standard instances are prof:Profiles instances
    for s, p, o in pg.triples((None, RDF.type, DCTERMS.Standard)):
        pg.add((s, RDF.type, PROF.Profile))
    # anything using prof:isProfileOf is a prof:Profile
    for s, p, o in pg.triples((None, PROF.isProfileOf, None)):
        pg.add((o, RDF.type, PROF.Profile))

    # type all RDs
    # anything indicated by prof:hasResource is a prof:ResourceDescriptor
    for s, p, o in pg.triples((None, PROF.hasResource, None)):
        pg.add((o, RDF.type, PROF.ResourceDescriptor))
