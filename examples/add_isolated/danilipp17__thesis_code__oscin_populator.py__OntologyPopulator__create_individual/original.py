# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._create_individual (lines 1065-1069, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

def _create_individual(self, prefix: str, key: str, owl_class: URIRef) -> URIRef:
    """Create a URI and declare its RDF:type."""
    uri = self.EX[f"{prefix}_{self._safe_id(key)}"]
    self.g.add((uri, RDF.type, owl_class))
    return uri
