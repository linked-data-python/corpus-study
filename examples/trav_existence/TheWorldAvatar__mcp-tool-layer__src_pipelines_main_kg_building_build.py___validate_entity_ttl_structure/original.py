# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/main_kg_building/build.py
# region: _validate_entity_ttl_structure (lines 854-914, stratum trav_existence)
# licence of the source repository: see meta.json
import os
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS
from context_shim import _resolve_expected_top_entity_uri  # context shim -- see meta.json

def _validate_entity_ttl_structure(
    *,
    ttl_path: str,
    entity_uri: str,
    entity_label: str,
    main_entity_policy: dict,
) -> tuple[bool, list[str]]:
    """
    Validate the published entity TTL against config-driven shell/link expectations.
    """
    shell_validation = (main_entity_policy or {}).get("shell_validation", {}) or {}
    messages: list[str] = []
    if not ttl_path or not os.path.exists(ttl_path):
        return False, [f"TTL not found for validation: {ttl_path}"]

    try:
        g = Graph()
        g.parse(ttl_path, format="turtle")
    except Exception as e:
        return False, [f"Failed to parse TTL: {e}"]

    top_class_iri = str(shell_validation.get("top_entity_class_iri") or "").strip()
    label_key_suffixes = shell_validation.get("label_key_suffixes_to_strip") or []
    if not isinstance(label_key_suffixes, list):
        label_key_suffixes = []
    resolved_entity_uri = _resolve_expected_top_entity_uri(
        g,
        top_class_iri=top_class_iri,
        entity_uri=entity_uri,
        entity_label=entity_label,
        label_key_suffixes_to_strip=label_key_suffixes,
    )
    top_entity = URIRef(resolved_entity_uri) if resolved_entity_uri else None
    if top_entity is not None and shell_validation.get("require_entity_uri_subject"):
        if not any(g.triples((top_entity, None, None))):
            messages.append(
                f"Missing top-level entity subject in TTL: {resolved_entity_uri or entity_uri}"
            )
        elif top_class_iri and (top_entity, RDF.type, URIRef(top_class_iri)) not in g:
            messages.append(
                f"Top-level entity missing required rdf:type: {top_class_iri}"
            )

    if top_entity is not None:
        for spec in shell_validation.get("required_links", []) or []:
            pred_iri = str((spec or {}).get("predicate_iri") or "").strip()
            target_class_iri = str((spec or {}).get("target_class_iri") or "").strip()
            min_count = int((spec or {}).get("min_count") or 0)
            if not pred_iri:
                continue
            pred = URIRef(pred_iri)
            objs = [o for o in g.objects(top_entity, pred) if isinstance(o, URIRef)]
            if target_class_iri:
                target_cls = URIRef(target_class_iri)
                objs = [o for o in objs if (o, RDF.type, target_cls) in g]
            if len(objs) < min_count:
                messages.append(
                    f"Missing required link {pred_iri}: expected >= {min_count}, found {len(objs)}"
                )

    return (len(messages) == 0), messages
