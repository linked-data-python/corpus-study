# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi/naas_abi/workflows/GetObjectPropertiesFromClassWorkflow.py
# region: GetObjectPropertiesFromClassWorkflow._process_ranges._get_labeled_uri (lines 259-263, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, Graph, URIRef

def _get_labeled_uri(uri):
    """Get label for a URI."""
    range_uri = URIRef(uri)
    range_label = self.graph.value(range_uri, RDFS.label)
    return {"uri": uri, "label": str(range_label) if range_label else None}
