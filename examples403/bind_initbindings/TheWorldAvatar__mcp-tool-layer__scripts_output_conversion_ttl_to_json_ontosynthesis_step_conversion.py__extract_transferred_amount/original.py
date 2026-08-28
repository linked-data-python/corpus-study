# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_step_conversion.py
# region: extract_transferred_amount (lines 366-412, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
from typing import Dict, List, Any, Optional

def extract_transferred_amount(graph: Graph, namespaces: Dict[str, Namespace], step_uri: str) -> str:
    """Extract transferred amount via ontosyn:hasTransferedAmount.
    Returns formatted string like "2.4 milliliter" or "N/A" if not found.
    """
    ontosyn = namespaces.get('ontosyn')
    if not ontosyn:
        return "N/A"

    query = """
    PREFIX ontosyn: <https://www.theworldavatar.com/kg/OntoSyn/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX om-2: <http://www.ontology-of-units-of-measure.org/resource/om-2/>

    SELECT DISTINCT ?val ?unit ?label WHERE {
      ?step ontosyn:hasTransferedAmount ?amount .
      OPTIONAL { ?amount om-2:hasNumericalValue ?val }
      OPTIONAL { ?amount om-2:hasUnit ?unit }
      OPTIONAL { ?amount rdfs:label ?label }
    } LIMIT 1
    """

    try:
        results = graph.query(query, initBindings={'step': URIRef(step_uri)})
    except Exception:
        results = []

    for row in results:
        label = str(row.label) if getattr(row, 'label', None) else ""

        # Prefer label if available and clean
        if label and not label.startswith("http"):
            return label

        # Otherwise construct from value and unit
        try:
            v = float(row.val) if getattr(row, 'val', None) is not None else None
        except Exception:
            v = None

        unit_iri = str(row.unit) if getattr(row, 'unit', None) else ""

        if v is not None:
            if unit_iri:
                return f"{v} {unit_iri}"
            return str(v)

    return "N/A"
