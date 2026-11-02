# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/step/step_details.py
# region: query_step_details_all_fields (lines 54-122, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import Any, Dict
from rdflib import Graph, URIRef
from step_details_context import _camelize, _local_name, query_step_type_label

def query_step_details_all_fields(graph: Graph, step_uri: str) -> Dict[str, Any]:
    """Collect all direct properties of a step, preferring labels for object IRIs.

    Output shape: { <StepTypeLabel>: { <fieldName>: value or [values] } }
    """
    step_type = query_step_type_label(graph, step_uri)

    # Query all outgoing properties except rdf:type
    q_props = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?p ?o ?olabel WHERE {
      ?s ?p ?o .
      FILTER(?p != rdf:type)
      OPTIONAL { ?o rdfs:label ?olabel }
    }
    """
    fields: Dict[str, Any] = {}
    for row in graph.query(q_props, initBindings={"s": URIRef(step_uri)}):
        # Normalize the object
        # Prefer human label when available; drop IRIs from final step field values
        value = str(row.olabel or "") if isinstance(row.o, URIRef) else str(row.o)
        fields.setdefault(_camelize(_local_name(str(row.p))), []).append(value)

    # Do not include raw URI in the output; keep only human-friendly fields

    # Attempt to surface the main rdfs:label for the step itself
    labels = [str(label) for label in graph.objects(
        URIRef(step_uri), URIRef("http://www.w3.org/2000/01/rdf-schema#label"))]
    if labels:
        # If multiple labels, keep them all
        fields["label"] = labels

    # Deduplicate object lists by label only
    for key, values in fields.items():
        merged_list = list(dict.fromkeys(value for value in values if value))
        fields[key] = values[0] if len(values) == 1 else (merged_list or values)

    return {step_type: fields}
