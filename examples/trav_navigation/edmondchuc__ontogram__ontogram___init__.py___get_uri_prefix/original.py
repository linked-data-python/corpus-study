# Extracted from edmondchuc/ontogram@777ea837bc : ontogram/__init__.py
# region: _get_uri_prefix (lines 85-100, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF, OWL, RDFS, DCTERMS
from ontogram.curies import CURIES

def _get_uri_prefix(uri : str, g):
    # Get the prefix of the URI.
    prefix = ''
    for k, v in CURIES.items():
        if v == uri:
            prefix = k
            return prefix

    # Didn't find a matching prefix in CURIES.
    # TODO: Do something here e.g. a lookup to prefix.cc or something else.
    for ontology, _, _ in g.triples((None, RDF.type, OWL.Ontology)):
        for preferred_prefix in g.objects(ontology, URIRef('http://purl.org/vocab/vann/preferredNamespacePrefix')):
            return preferred_prefix

    # Nothing was found, just return an empty string.
    return prefix
