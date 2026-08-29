# Extracted from mupparapusamuel/semantica@873e3aa318 : semantica/ingest/ontology_ingestor.py
# region: OntologyIngestor._add_property (lines 355-386, stratum trav_one_step)
# licence of the source repository: see meta.json
from typing import Any, Dict, List, Optional, Union
import rdflib
from rdflib import RDF, RDFS, OWL, Graph

def _add_property(self, graph: Graph, subject: rdflib.term.Node, prop_type: str, properties_dict: Dict):
    if isinstance(subject, rdflib.BNode):
        return

    uri = str(subject)
    if uri in properties_dict:
        return

    prop_def = {
        "uri": uri,
        "name": self._get_local_name(uri),
        "type": prop_type
    }

    label = graph.value(subject, RDFS.label)
    if label:
        prop_def["label"] = str(label)

    comment = graph.value(subject, RDFS.comment)
    if comment:
        prop_def["description"] = str(comment)

    # Domain and Range
    domain = graph.value(subject, RDFS.domain)
    if domain and isinstance(domain, rdflib.URIRef):
        prop_def["domain"] = str(domain)

    range_val = graph.value(subject, RDFS.range)
    if range_val and isinstance(range_val, rdflib.URIRef):
        prop_def["range"] = str(range_val)

    properties_dict[uri] = prop_def
