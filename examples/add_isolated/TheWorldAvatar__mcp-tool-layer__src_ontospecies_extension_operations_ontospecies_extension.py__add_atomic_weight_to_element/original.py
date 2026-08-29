# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/ontospecies_extension/operations/ontospecies_extension.py
# region: add_atomic_weight_to_element (lines 566-587, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from context_shim import OS, locked_graph, _safe_parent, _mint_hash_iri, _ensure_type_with_label, _class

def add_atomic_weight_to_element(element_iri: str, value) -> str:
    """
    Attach atomic weight to an element node. Handles both float and "N/A" values.
    """
    with locked_graph() as g:
        parent = _safe_parent(element_iri)
        if parent is None:
            return "element IRI must be absolute https IRI"
        aw = _mint_hash_iri("AtomicWeight")
        # Compose label
        label = f"Atomic Weight {value if value != 'N/A' else 'N/A'}"
        _ensure_type_with_label(g, aw, _class(OS, "AtomicWeight"), label)
        # Handle N/A specially as a string literal; otherwise use float datatype
        if value == "N/A":
            g.set((aw, _class(OS, "hasAtomicWeightValue"), Literal("N/A")))
        else:
            try:
                g.set((aw, _class(OS, "hasAtomicWeightValue"), Literal(float(value), datatype=XSD.float)))
            except Exception:
                return f"Invalid atomic weight value: {value!r}"
        g.add((parent, _class(OS, "hasAtomicWeight"), aw))
        return str(aw)
