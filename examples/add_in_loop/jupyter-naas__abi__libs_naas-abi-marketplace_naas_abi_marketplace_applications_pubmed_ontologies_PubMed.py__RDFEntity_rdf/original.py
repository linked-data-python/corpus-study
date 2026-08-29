# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/pubmed/ontologies/PubMed.py
# region: RDFEntity.rdf (lines 37-70, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

def rdf(self, subject_uri: str | None = None) -> Graph:
    """Generate RDF triples for this instance"""
    g = Graph()

    # Use stored URI or provided subject_uri
    if subject_uri is None:
        subject_uri = self._uri
    subject = URIRef(subject_uri)

    # Add class type
    if hasattr(self, '_class_uri'):
        g.add((subject, RDF.type, URIRef(self._class_uri)))

    # Add properties
    if hasattr(self, '_property_uris'):
        for prop_name, prop_uri in self._property_uris.items():
            prop_value = getattr(self, prop_name, None)
            if prop_value is not None:
                if isinstance(prop_value, list):
                    for item in prop_value:
                        if hasattr(item, 'rdf'):
                            # Add triples from related object
                            g += item.rdf()
                            g.add((subject, URIRef(prop_uri), URIRef(item._uri)))
                        else:
                            g.add((subject, URIRef(prop_uri), Literal(item)))
                elif hasattr(prop_value, 'rdf'):
                    # Add triples from related object
                    g += prop_value.rdf()
                    g.add((subject, URIRef(prop_uri), URIRef(prop_value._uri)))
                else:
                    g.add((subject, URIRef(prop_uri), Literal(prop_value)))

    return g
