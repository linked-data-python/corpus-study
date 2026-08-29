# Extracted from kracr/cog-csv-owl-bridge@d238191ecc : src/csv_to_owl/csv_owl_code.py
# region: csv_to_owl_subclass (lines 266-380, stratum add_isolated)
# licence of the source repository: see meta.json
import pandas as pd
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib import Graph, Namespace
from rdflib import Graph, Namespace
from rdflib import URIRef, RDF, RDFS, Namespace

def csv_to_owl_subclass(subclass_csv_file: str, prefix_file: str, output_file="subclass.owl"):
    g = Graph()
    prefixes, xml_base = load_prefixes(prefix_file)
    _bind_prefixes_to_graph(g, prefixes)
    try:
        df = pd.read_csv(subclass_csv_file, dtype=str).fillna("")
    except FileNotFoundError:
        print(f"[WARN] subclass CSV '{subclass_csv_file}' not found — skipping subclasses.")
        return
    except Exception as e:
        print(f"[ERROR] reading subclass CSV '{subclass_csv_file}': {e}")
        return

    def find_col(cols, candidates):
        for cand in candidates:
            for c in cols:
                if c.lower().strip() == cand.lower().strip():
                    return c
        return None

    subj_col = find_col(df.columns, ["Subclass", "subclass"])
    super_col = find_col(df.columns, ["Superclass", "superclass"])
    prop_col = find_col(df.columns, ["Restriction (onProperty)", "onProperty", "Restriction (onproperty)", "on_property"])
    quant_col = find_col(df.columns, ["Restriction (quantifier)", "quantifier", "Restriction (quantifier)"])

    def build_restriction(prop_uri, quantifier, filler_uri):
        b = BNode()
        g.add((b, RDF.type, OWL.Restriction))
        g.add((b, OWL.onProperty, prop_uri))
        if quantifier == "some":
            g.add((b, OWL.someValuesFrom, filler_uri))
        else:
            g.add((b, OWL.allValuesFrom, filler_uri))
        return b

    for row_idx, row in df.iterrows():
        subclass_str = (row.get(subj_col, "") or "").strip()
        superclass_str = (row.get(super_col, "") or "").strip()
        on_property_str = (row.get(prop_col, "") or "").strip()
        quantifier = (row.get(quant_col, "") or "").strip().lower()

        on_property_uri = resolve_uri(on_property_str, prefixes) if on_property_str else None
        superclass_uri = resolve_uri(superclass_str, prefixes) if superclass_str else None

        # textual restriction in subclass column => create anonymous restriction ⊑ Superclass (GCI)
        if subclass_str and (" some " in subclass_str or " all " in subclass_str):
            if " some " in subclass_str:
                parts = subclass_str.split(" some ", 1); q = "some"
            else:
                parts = subclass_str.split(" all ", 1); q = "all"
            prop_part = parts[0].strip()
            fill_part = parts[1].strip() if len(parts) > 1 else ""
            prop_uri = resolve_uri(prop_part, prefixes) if prop_part else None
            filler_uri = resolve_uri(fill_part, prefixes) if fill_part else None
            if prop_uri and filler_uri and superclass_uri:
                restriction_bnode = build_restriction(prop_uri, q, filler_uri)
                # Do NOT declare the restriction bnode (anonymous). Declare only named IRIs.
                ensure_declaration(g, prop_uri, OWL.ObjectProperty)
                ensure_declaration(g, filler_uri, OWL.Class)
                ensure_declaration(g, superclass_uri, OWL.Class)
                g.add((restriction_bnode, RDFS.subClassOf, superclass_uri))
                continue
            else:
                print(f"[WARN] Could not resolve textual restriction in Subclass column (row {row_idx}): '{subclass_str}'")

        # intersection A & B ⊑ C
        if subclass_str and "&" in subclass_str:
            parts = [p.strip() for p in subclass_str.split("&") if p.strip()]
            class_uris = [resolve_uri(p, prefixes) for p in parts]
            class_uris = [u for u in class_uris if u is not None]
            for cls in class_uris:
                ensure_declaration(g, cls, OWL.Class)
            anon_cls = BNode()
            g.add((anon_cls, OWL.intersectionOf, reconstruct_intersection(g, class_uris)))
            if superclass_uri:
                g.add((anon_cls, RDFS.subClassOf, superclass_uri))
            continue

        # A ⊑ (∃R.C) or (∀R.C)
        if subclass_str and on_property_uri and quantifier and superclass_uri:
            subclass_uri = resolve_uri(subclass_str, prefixes)
            restriction = BNode()
            g.add((restriction, RDF.type, OWL.Restriction))
            g.add((restriction, OWL.onProperty, on_property_uri))
            if quantifier == "some":
                g.add((restriction, OWL.someValuesFrom, superclass_uri))
            else:
                g.add((restriction, OWL.allValuesFrom, superclass_uri))
            ensure_declaration(g, subclass_uri, OWL.Class)
            ensure_declaration(g, on_property_uri, OWL.ObjectProperty)
            ensure_declaration(g, superclass_uri, OWL.Class)
            g.add((subclass_uri, RDFS.subClassOf, restriction))
            continue

        # GCI row: empty Subclass but restriction columns filled -> restriction ⊑ Superclass
        if (not subclass_str) and on_property_uri and quantifier and superclass_uri:
            restriction_bnode = build_restriction(on_property_uri, quantifier, superclass_uri)
            ensure_declaration(g, on_property_uri, OWL.ObjectProperty)
            ensure_declaration(g, superclass_uri, OWL.Class)
            g.add((restriction_bnode, RDFS.subClassOf, superclass_uri))
            continue

        # Simple A ⊑ B
        if subclass_str and superclass_uri:
            subclass_uri = resolve_uri(subclass_str, prefixes)
            ensure_declaration(g, subclass_uri, OWL.Class)
            ensure_declaration(g, superclass_uri, OWL.Class)
            g.add((subclass_uri, RDFS.subClassOf, superclass_uri))
            continue

        if any([subclass_str, on_property_str, superclass_str, quantifier]):
            print(f"[WARN] Unhandled subclass row {row_idx}: Subclass='{subclass_str}', onProperty='{on_property_str}', quantifier='{quantifier}', Superclass='{superclass_str}'")

    g.serialize(destination=output_file, format='xml')
    print(f"✅ Subclass triples written to {output_file}")
