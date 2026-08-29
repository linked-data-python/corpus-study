# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_tasks/construction/json_to_rdf.py
# region: json_to_rdf2.add_entity (lines 321-408, stratum add_in_loop)
# licence of the source repository: see meta.json
import re, uuid
from typing import Any, Dict, Tuple, Optional, Iterable, List, Mapping
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, XSD
Provenance = Mapping[str, str]  # json_path -> source_uri_or_bnode
EXC = Namespace("http://ex.com/source/class/")

def add_entity(o: Dict[str, Any], kind: str, generate_type: bool = False, 
               current_path: str = "$", parent_provenance: Optional[Provenance] = None) -> URIRef:
    # Generate unique URI based on path and content hash
    import hashlib
    content_hash = hashlib.md5(str(o).encode()).hexdigest()
    s = URIRef(f"http://example.com/test/{content_hash}")
    if generate_type:
        g.add((s, RDF.type, URIRef(f"{EXC}{kind}")))

    # Record provenance for this entity
    if trace and provenance is not None:
        provenance[current_path] = str(s)

    # Root/entity labels
    lab = find_labelish_value(o)
    if lab:
        g.add((s, RDFS.label, Literal(lab)))
        # g.add((s, SKOS.prefLabel, Literal(lab)))

    for k, v in o.items():
        k_norm = re.sub(r"\s+", "_", _norm_key(k).lower())
        p_obj  = _prop_uri(k_norm)
        relation_provenance[k] = str(p_obj)
        # p_lit  = _prop_lit_uri(k_norm)

        # Decide based on heuristic
        decision, score, _ = heuristic_decide_object_vs_literal(k, v)

        # Case 1: literal-ish
        if decision == "literal":
            if isinstance(v, list):
                for item in v:
                    if item is not None and not isinstance(item, dict):
                        g.add((s, p_obj, _literal(item)))
            elif not isinstance(v, dict):
                g.add((s, p_obj, _literal(v)))

        else:
            # Case 2: object-ish
            if isinstance(v, dict):
                prop_path = f"{current_path}.{k}"
                o2 = add_entity(v, kind=k_norm.capitalize(), 
                               current_path=prop_path, parent_provenance=provenance)
                g.add((s, p_obj, o2))
            elif isinstance(v, list):
                # emit verbatim literals for provenance/compat, and mint nodes where possible
                for idx, item in enumerate(v):
                    item_path = f"{current_path}.{k}[{idx}]"
                    if isinstance(item, dict):
                        o2 = add_entity(item, kind=k_norm.capitalize(),
                                       current_path=item_path, parent_provenance=provenance)
                        g.add((s, p_obj, o2))
                    elif isinstance(item, (str, int, float)) and str(item).strip():
                        # provenance literal
                        # g.add((s, p_lit, _literal(item)))
                        # mint a node with label if it looks like an entity-ish string
                        lab_str = str(item).strip()
                        item_hash = hashlib.md5(lab_str.encode()).hexdigest()
                        o2 = URIRef(f"http://example.com/test/{item_hash}")
                        g.add((o2, RDFS.label, Literal(lab_str)))

                        if generate_type:
                            g.add((o2, RDF.type, URIRef(f"{EXC}{k_norm.capitalize()}")))    
                        # g.add((o2, SKOS.prefLabel, Literal(lab_str)))
                        g.add((s, p_obj, o2))

                        # Record provenance for list item
                        if trace and provenance is not None:
                            provenance[item_path] = str(o2)
            else:
                # single primitive that looks like an entity name → dual representation
                if v is not None and str(v).strip():
                    prop_path = f"{current_path}.{k}"
                    # g.add((s, p_lit, _literal(v)))  # keep raw literal
                    lab_str = str(v).strip()
                    item_hash = hashlib.md5(lab_str.encode()).hexdigest()[:8]
                    o2 = URIRef(f"http://example.com/test/{item_hash}")
                    g.add((o2, RDFS.label, Literal(lab_str)))
                    if generate_type:
                        g.add((o2, RDF.type, URIRef(f"{EXC}{k_norm.capitalize()}")))    
                    # g.add((o2, SKOS.prefLabel, Literal(lab_str)))
                    g.add((s, p_obj, o2))

                    # Record provenance for single primitive
                    if trace and provenance is not None:
                        provenance[prop_path] = str(o2)

    return s
