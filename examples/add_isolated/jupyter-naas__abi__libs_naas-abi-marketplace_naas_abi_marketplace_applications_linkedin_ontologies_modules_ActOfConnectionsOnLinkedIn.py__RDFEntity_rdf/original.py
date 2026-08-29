# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/linkedin/ontologies/modules/ActOfConnectionsOnLinkedIn.py
# region: RDFEntity.rdf (lines 40-120, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
BFO = Namespace("http://purl.obolibrary.org/obo/")
ABI = Namespace("http://ontology.naas.ai/abi/")
CCO = Namespace("https://www.commoncoreontologies.org/")

def rdf(
    self, subject_uri: str | None = None, visited: set[str] | None = None
) -> Graph:
    """Generate RDF triples for this instance

    Args:
        subject_uri: Optional URI to use as subject (defaults to self._uri)
        visited: Set of URIs that have already been processed (for cycle detection)
    """
    # Initialize visited set if not provided
    if visited is None:
        visited = set()

    g = Graph()
    g.bind("cco", CCO)
    g.bind("bfo", BFO)
    g.bind("abi", ABI)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)

    # Use stored URI or provided subject_uri
    if subject_uri is None:
        subject_uri = self._uri
    subject = URIRef(subject_uri)

    # Check if we've already processed this entity (cycle detection)
    if subject_uri in visited:
        # Already processed, just return empty graph to avoid infinite recursion
        # The relationship triple will be added by the caller
        return g

    # Mark this entity as visited before processing
    visited.add(subject_uri)

    # Add class type
    if hasattr(self, "_class_uri"):
        g.add((subject, RDF.type, URIRef(self._class_uri)))

    # Add owl:NamedIndividual type
    g.add((subject, RDF.type, OWL.NamedIndividual))

    # Add label if it exists
    if hasattr(self, "label"):
        g.add((subject, RDFS.label, Literal(self.label)))

    object_props: set[str] = getattr(self, "_object_properties", set())

    # Add properties
    if hasattr(self, "_property_uris"):
        for prop_name, prop_uri in self._property_uris.items():
            is_object_prop = prop_name in object_props
            prop_value = getattr(self, prop_name, None)
            if prop_value is not None:
                if isinstance(prop_value, list):
                    for item in prop_value:
                        if hasattr(item, "rdf") and hasattr(item, "_uri"):
                            # Check if this entity was already visited to prevent cycles
                            if item._uri not in visited:
                                # Add triples from related object
                                g += item.rdf(visited=visited)
                            # Always add the triple, even if already visited
                            g.add((subject, URIRef(prop_uri), URIRef(item._uri)))
                        elif is_object_prop and isinstance(item, (str, URIRef)):
                            g.add((subject, URIRef(prop_uri), URIRef(str(item))))
                        else:
                            g.add((subject, URIRef(prop_uri), Literal(item)))
                elif hasattr(prop_value, "rdf") and hasattr(prop_value, "_uri"):
                    # Check if this entity was already visited to prevent cycles
                    if prop_value._uri not in visited:
                        # Add triples from related object
                        g += prop_value.rdf(visited=visited)
                    # Always add the triple, even if already visited
                    g.add((subject, URIRef(prop_uri), URIRef(prop_value._uri)))
                elif is_object_prop and isinstance(prop_value, (str, URIRef)):
                    g.add((subject, URIRef(prop_uri), URIRef(str(prop_value))))
                else:
                    g.add((subject, URIRef(prop_uri), Literal(prop_value)))

    return g
