# Extracted from ktbs/ktbs@4f9f50c770 : utest/example1.py
# region: GroupImplementation.create_service_root (lines 413-419, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, RDF, URIRef

@classmethod
def create_service_root(cls, service):
    """Create a root-group in given service"""
    root_uri = service.root_uri
    graph = Graph(identifier=root_uri)
    graph.add((root_uri, RDF.type, cls.RDF_MAIN_TYPE))
    cls.create(service, root_uri, graph)
