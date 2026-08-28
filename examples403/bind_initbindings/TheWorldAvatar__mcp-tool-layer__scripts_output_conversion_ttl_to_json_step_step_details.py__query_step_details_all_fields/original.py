# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/step/step_details.py
# region: query_step_details_all_fields (lines 54-122, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import Any, Dict, List
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
      FILTER(?s = ?S)
      FILTER(?p != rdf:type)
      OPTIONAL { ?o rdfs:label ?olabel }
    }
    """
    results = graph.query(q_props, initBindings={"S": URIRef(step_uri)})

    fields: Dict[str, Any] = {}
    for row in results:
        p_uri = str(row.p)
        o = row.o
        o_label = str(row.olabel) if row.olabel else ""
        field_name = _camelize(_local_name(p_uri))

        # Normalize the object
        if isinstance(o, URIRef):
            # Prefer human label when available; drop IRIs from final step field values
            value = o_label or ""
        else:
            value = str(o)

        if field_name in fields:
            # Merge: list-append when already present
            if isinstance(fields[field_name], list):
                fields[field_name].append(value)
            else:
                fields[field_name] = [fields[field_name], value]
        else:
            fields[field_name] = value

    # Do not include raw URI in the output; keep only human-friendly fields

    # Attempt to surface the main rdfs:label for the step itself
    q_label = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label WHERE { ?s rdfs:label ?label . FILTER(?s = ?S) }
    """
    labels = [str(r.label) for r in graph.query(q_label, initBindings={"S": URIRef(step_uri)})]
    if labels:
        # If multiple labels, keep them all
        fields["label"] = labels if len(labels) > 1 else labels[0]

    # Deduplicate object lists by label only
    for key, value in list(fields.items()):
        if isinstance(value, list):
            seen: List[str] = []
            merged_list: List[str] = []
            for it in value:
                lbl = it if isinstance(it, str) else ""
                if lbl and lbl not in seen:
                    seen.append(lbl)
                    merged_list.append(lbl)
            if merged_list:
                fields[key] = merged_list

    return {step_type: fields}
