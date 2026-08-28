# Extracted from mupparapusamuel/semantica@873e3aa318 : semantica/ingest/ontology_ingestor.py
# region: OntologyIngestor._convert_to_dict (lines 252-353, stratum trav_navigation)
# licence of the source repository: see meta.json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import rdflib
from rdflib import RDF, RDFS, OWL, Graph

def _convert_to_dict(self, graph: Graph, source_path: str, format: str = "unknown") -> Dict[str, Any]:
    """
    Convert rdflib Graph to Semantica ontology dictionary.

    Args:
        graph: Parsed rdflib Graph
        source_path: Source file path
        format: Format of the ontology file

    Returns:
        Ontology dictionary
    """
    ontology = {
        "uri": "",
        "name": os.path.basename(source_path),
        "version": "1.0",
        "classes": [],
        "properties": [],
        "metadata": {
            "source_path": source_path,
            "ingested_at": datetime.now().isoformat(),
            "format": format
        }
    }

    # 1. Extract Ontology Metadata
    for s, p, o in graph.triples((None, RDF.type, OWL.Ontology)):
        ontology["uri"] = str(s)

        # Try to find label/comment/versionInfo
        for _, _, label in graph.triples((s, RDFS.label, None)):
            ontology["name"] = str(label)

        for _, _, comment in graph.triples((s, RDFS.comment, None)):
            ontology["description"] = str(comment)

        for _, _, version in graph.triples((s, OWL.versionInfo, None)):
            ontology["version"] = str(version)

        # Break after first ontology definition found (usually only one per file)
        break

    # 2. Extract Classes
    classes = {}
    # Union of owl:Class and rdfs:Class
    class_types = [OWL.Class, RDFS.Class]
    for c_type in class_types:
        for s, p, o in graph.triples((None, RDF.type, c_type)):
            if isinstance(s, rdflib.BNode):
                continue # Skip blank nodes for now

            uri = str(s)
            if uri not in classes:
                cls_def = {
                    "uri": uri,
                    "name": self._get_local_name(uri),
                    "type": "class"
                }

                # Add label/comment
                label = graph.value(s, RDFS.label)
                if label:
                    cls_def["label"] = str(label)
                    cls_def["name"] = str(label) # Prefer label as name if available? Or keep URI fragment? 
                    # Keeping local name from URI is safer for internal IDs, label for display. 
                    # But Semantica seems to use "name" for the identifier in some examples.
                    # Let's keep name as local name or label if simple.

                comment = graph.value(s, RDFS.comment)
                if comment:
                    cls_def["description"] = str(comment)

                # Superclasses
                parents = []
                for _, _, parent in graph.triples((s, RDFS.subClassOf, None)):
                    if isinstance(parent, rdflib.URIRef):
                        parents.append(str(parent))
                if parents:
                    cls_def["parents"] = parents

                classes[uri] = cls_def

    ontology["classes"] = list(classes.values())

    # 3. Extract Properties
    properties = {}
    # Object Properties
    for s, p, o in graph.triples((None, RDF.type, OWL.ObjectProperty)):
        self._add_property(graph, s, "object", properties)

    # Datatype Properties
    for s, p, o in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
        self._add_property(graph, s, "data", properties)

    # RDF Properties (generic)
    for s, p, o in graph.triples((None, RDF.type, RDF.Property)):
        if str(s) not in properties: # Don't overwrite if already found as specific type
            self._add_property(graph, s, "annotation", properties) # Default to annotation or generic

    ontology["properties"] = list(properties.values())

    return ontology
