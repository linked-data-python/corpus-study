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
    shell_validation = (main_entity_policy or {}).get("shell_validation") or {}
    if not ttl_path or not os.path.exists(ttl_path):
        return False, [f"TTL not found for validation: {ttl_path}"]

    try:
        g = Graph().parse(ttl_path, format="turtle")
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
    if not resolved_entity_uri:
        return True, []
    top_entity = URIRef(resolved_entity_uri)
    messages: list[str] = []
    if shell_validation.get("require_entity_uri_subject"):
        if (top_entity, None, None) not in g:
            messages.append(f"Missing top-level entity subject in TTL: {resolved_entity_uri}")
        elif top_class_iri and (top_entity, RDF.type, URIRef(top_class_iri)) not in g:
            messages.append(f"Top-level entity missing required rdf:type: {top_class_iri}")

    for spec in shell_validation.get("required_links") or []:
        spec = spec or {}
        pred_iri = str(spec.get("predicate_iri") or "").strip()
        target_class_iri = str(spec.get("target_class_iri") or "").strip()
        min_count = int(spec.get("min_count") or 0)
        if not pred_iri:
            continue
        objs = [o for o in g.objects(top_entity, URIRef(pred_iri)) if isinstance(o, URIRef)
                and (not target_class_iri or (o, RDF.type, URIRef(target_class_iri)) in g)]
        if len(objs) < min_count:
            messages.append(
                f"Missing required link {pred_iri}: expected >= {min_count}, found {len(objs)}"
            )

    return not messages, messages
