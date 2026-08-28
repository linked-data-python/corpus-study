# Extracted from boricles/ontosphere@e055553268 : backend/app/services/diff_service.py
# region: _extract_from_jsonld (lines 36-120, stratum trav_navigation)
# licence of the source repository: see meta.json
import json

def _extract_from_jsonld(jsonld_data: dict) -> tuple[list[dict], list[dict]]:
    """Parse a JSON-LD snapshot via rdflib and return (nodes, edges)."""
    from rdflib import BNode, Graph as RdfGraph
    from rdflib.namespace import OWL, RDF, RDFS

    g = RdfGraph()
    g.parse(data=json.dumps(jsonld_data), format="json-ld")

    nodes: list[dict] = []
    edges: list[dict] = []
    seen_uris: set[str] = set()

    # --- Classes ---
    for subj in g.subjects(RDF.type, OWL.Class):
        if isinstance(subj, BNode):
            continue
        uri = str(subj)
        if uri in seen_uris:
            continue
        seen_uris.add(uri)
        label = str(g.value(subj, RDFS.label, default=""))
        description = str(g.value(subj, RDFS.comment, default=""))
        nodes.append({
            "uri": uri,
            "label": label,
            "description": description,
            "node_type": "class",
        })

    # --- subClassOf relationships ---
    for subj, obj in g.subject_objects(RDFS.subClassOf):
        if isinstance(subj, BNode) or isinstance(obj, BNode):
            continue
        edges.append({
            "source_uri": str(subj),
            "target_uri": str(obj),
            "edge_type": "SUBCLASS_OF",
        })

    # --- equivalentClass relationships ---
    for subj, obj in g.subject_objects(OWL.equivalentClass):
        if isinstance(subj, BNode) or isinstance(obj, BNode):
            continue
        edges.append({
            "source_uri": str(subj),
            "target_uri": str(obj),
            "edge_type": "EQUIVALENT_TO",
        })

    # --- disjointWith relationships ---
    for subj, obj in g.subject_objects(OWL.disjointWith):
        if isinstance(subj, BNode) or isinstance(obj, BNode):
            continue
        edges.append({
            "source_uri": str(subj),
            "target_uri": str(obj),
            "edge_type": "DISJOINT_WITH",
        })

    # --- ObjectProperty nodes ---
    for subj in g.subjects(RDF.type, OWL.ObjectProperty):
        if isinstance(subj, BNode):
            continue
        uri = str(subj)
        if uri in seen_uris:
            continue
        seen_uris.add(uri)
        label = str(g.value(subj, RDFS.label, default=""))
        description = str(g.value(subj, RDFS.comment, default=""))
        domain = g.value(subj, RDFS.domain)
        range_val = g.value(subj, RDFS.range)
        nodes.append({
            "uri": uri,
            "label": label,
            "description": description,
            "node_type": "property",
        })
        if domain and range_val:
            edges.append({
                "source_uri": str(domain),
                "target_uri": str(range_val),
                "edge_type": "HAS_PROPERTY",
            })

    return nodes, edges
