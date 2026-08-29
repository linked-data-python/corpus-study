# Extracted from linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/owlgen.py
# region: OwlSchemaGenerator._some_values_from (lines 1392-1401, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, OWL, RDF, XSD, BNode, Graph, Literal, URIRef
OWL_EXPRESSION: TypeAlias = BNode | URIRef

def _some_values_from(self, property_uri: URIRef, filler: OWL_EXPRESSION) -> BNode:
    if not property_uri:
        raise ValueError(f"Property is required, filler: {filler}")
    if not filler:
        raise ValueError(f"Filler is required, property: {property_uri}")
    node = BNode()
    self.graph.add((node, RDF.type, OWL.Restriction))
    self.graph.add((node, OWL.onProperty, property_uri))
    self.graph.add((node, OWL.someValuesFrom, filler))
    return node
