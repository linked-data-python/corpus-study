# Extracted from d3fend/d3fend-ontology@cce593d61c : src/util/dashboard_report.py
# region: ontology_label (lines 571-573, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS

def ontology_label(graph, iri):
    label = graph.value(URIRef(iri), RDFS.label)
    return text_value(label) or compact_uri(iri)
