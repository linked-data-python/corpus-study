# Extracted from acdh-oeaw/vocabseditor@bf418c87b3 : vocabs/rdf_utils.py
# region: graph_construct_qs (lines 27-53, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from rdflib import Literal, Namespace, URIRef
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")

def graph_construct_qs(results):
    main_concept_scheme = results.first().scheme.get_subject()
    g = rdflib.Graph() + results.first().scheme.as_graph()
    for obj in results:
        g.add((URIRef(obj.create_uri()), SKOS.inScheme, main_concept_scheme))
        g += obj.as_graph()
        for x in obj.collection.all():
            collection = x.get_subject()
            g += x.as_graph()
            for predicate, names in ((DC.creator, x.creator), (DC.contributor, x.contributor)):
                if names:
                    for i in names.split(";"):
                        g.add((collection, predicate, Literal(i.strip())))
            for y in x.has_members.all():
                g.add((collection, SKOS.member, URIRef(y.legacy_id or y.create_uri())))
    return g
