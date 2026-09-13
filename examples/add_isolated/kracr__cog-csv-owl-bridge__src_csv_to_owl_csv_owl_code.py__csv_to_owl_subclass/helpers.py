# Context shim (see meta.json): the module-level helpers that
# csv_to_owl_subclass calls (load_prefixes, _bind_prefixes_to_graph,
# resolve_uri, ensure_declaration, reconstruct_intersection,
# normalize_ns_for_join) live ABOVE the extracted region in the same file,
# src/csv_to_owl/csv_owl_code.py of kracr/cog-csv-owl-bridge@d238191ecc.
# Copied verbatim (not reimplemented) so the region executes standalone.
# Identical bindings for both representations.
from rdflib import Graph, Namespace, URIRef, BNode
from rdflib.namespace import RDF, OWL
from rdflib.collection import Collection
from typing import Dict, Optional


def normalize_ns_for_join(ns: str) -> str:
    if ns is None:
        return ""
    return str(ns).strip()


def load_prefixes(prefix_file: str):
    """
    Reads a CSV of prefixes. Expected rows: prefix, namespace
    Returns (prefix_map, xml_base) where xml_base is the value for xml:base if present.
    """
    prefix_map = {}
    xml_base = None
    try:
        import csv
        with open(prefix_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = [r for r in reader if any(cell.strip() for cell in r)]
            if not rows:
                return prefix_map, xml_base

            # detect header heuristics (prefix, namespace)
            first = rows[0]
            data_rows = rows
            if len(first) >= 2 and first[0].strip().lower() in ('prefix', 'pref') and first[1].strip().lower() in ('namespace', 'ns', 'iri'):
                data_rows = rows[1:]

            for r in data_rows:
                if len(r) < 2:
                    continue
                raw_pref = r[0].strip()
                raw_ns = r[1].strip()
                if raw_pref.lower() == 'xml:base':
                    xml_base = raw_ns
                else:
                    # normalize the default marker to empty string key
                    if raw_pref in ("", ":", "default"):
                        key = ""
                    else:
                        key = raw_pref
                    prefix_map[key] = raw_ns
    except FileNotFoundError:
        print(f"[WARN] Prefix file '{prefix_file}' not found.")
    except Exception as e:
        print(f"[ERROR] Error reading prefix file '{prefix_file}': {e}")

    # debug printing: include xml:base in count display so terminal shows what you expect
    total_count = len(prefix_map) + (1 if xml_base else 0)
    print(f"[DEBUG] Loaded prefixes (count={total_count}):")
    for k, v in prefix_map.items():
        display_k = ':' if k == '' else k
        print(f"    prefix='{display_k}' -> '{v}'")
    if xml_base:
        print(f"    prefix='xml:base' -> '{xml_base}'")
        print(f"[DEBUG] xml:base = '{xml_base}'")
    return prefix_map, xml_base


def _bind_prefixes_to_graph(g: Graph, prefixes_map):
    """
    Bind prefixes to rdflib Graph. prefixes_map keys may include empty string for default prefix.
    rdflib.bind allows an empty string to denote the default prefix. However it does not accept ':'.
    This function maps ':'/illegal tokens into a safe name for binding but preserves the mapping
    semantics by using the original namespace.
    """
    bound_count = 0
    print("[INFO] Number of items in prefix map:", len(prefixes_map))
    for prefix_key, ns in prefixes_map.items():
        try:
            bind_name = prefix_key
            if bind_name == "":
                bound_count += 1
                g.bind('', Namespace(ns))
            else:
                safe = bind_name.replace(':', '_').replace(' ', '_')
                if not safe:
                    safe = 'ns'
                bound_count += 1
                g.bind(safe, Namespace(ns))
        except Exception as e:
            print(f"[WARN] Could not bind prefix '{prefix_key}' -> '{ns}': {e}")

    print(f"[INFO] Successfully bound {bound_count} prefixes.")


def resolve_uri(name: Optional[str], prefixes: Dict[str, str]) -> Optional[URIRef]:
    if name is None:
        return None
    text = str(name).strip()
    if not text:
        return None
    if text.startswith("http://") or text.startswith("https://"):
        return URIRef(text)
    if ":" not in text:
        default_ns = prefixes.get("", None)
        if default_ns:
            ns = normalize_ns_for_join(default_ns)
            sep = "" if ns.endswith(('#', '/')) else '#'
            return URIRef(ns + sep + text)
        print(f"[WARN] Bare name '{text}' encountered but no default prefix defined. Returning raw URIRef.")
        return URIRef(text)
    prefix, local = text.split(":", 1)
    if prefix in ("", ":"):
        ns = prefixes.get("", None)
    else:
        ns = prefixes.get(prefix, None)
    if not ns:
        print(f"[WARN] Prefix '{prefix}' not found when resolving '{text}'. Returning raw URIRef.")
        return URIRef(text)
    ns_norm = normalize_ns_for_join(ns)
    sep = "" if ns_norm.endswith(('#', '/')) else '#'
    return URIRef(ns_norm + sep + local)


def ensure_declaration(g: Graph, uri: Optional[URIRef], rdf_type):
    """
    Only add declaration if uri is a named URIRef (not a BNode).
    This avoids inflating 'declaration axiom' counts by declaring anonymous restriction nodes.
    """
    if uri is not None and isinstance(uri, URIRef):
        g.add((uri, RDF.type, rdf_type))


def reconstruct_intersection(g: Graph, uris):
    bnode = BNode()
    Collection(g, bnode, uris)
    return bnode
