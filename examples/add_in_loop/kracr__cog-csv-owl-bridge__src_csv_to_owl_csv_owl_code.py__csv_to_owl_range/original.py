# Extracted from kracr/cog-csv-owl-bridge@d238191ecc : src/csv_to_owl/csv_owl_code.py
# region: csv_to_owl_range (lines 416-448, stratum add_in_loop)
# licence of the source repository: see meta.json
import csv
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib import Graph, Namespace
from rdflib import Graph, Namespace
from rdflib import URIRef, RDF, RDFS, Namespace

def csv_to_owl_range(range_csv_file: str, prefix_file: str, output_file="range.owl"):
    g = Graph()
    prefixes, xml_base = load_prefixes(prefix_file)
    _bind_prefixes_to_graph(g, prefixes)
    try:
        with open(range_csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            colnames = list(reader.fieldnames or [])
            prop_col = None; range_col = None
            for c in colnames:
                lc = c.lower().strip()
                if lc in ("object","property","prop","predicate"):
                    prop_col = c
                if lc in ("range","class","range_class"):
                    range_col = c
            if prop_col is None and colnames:
                prop_col = colnames[0]
            if range_col is None and len(colnames) > 1:
                range_col = colnames[1]
            for row in reader:
                prop_uri = resolve_uri(row.get(prop_col, ""), prefixes)
                rng_uri = resolve_uri(row.get(range_col, ""), prefixes)
                ensure_declaration(g, prop_uri, OWL.ObjectProperty)
                ensure_declaration(g, rng_uri, OWL.Class)
                g.add((prop_uri, RDFS.range, rng_uri))
    except FileNotFoundError:
        print(f"[WARN] range CSV '{range_csv_file}' not found — skipping range.")
        return
    except Exception as e:
        print(f"[ERROR] reading range CSV '{range_csv_file}': {e}")
        return
    g.serialize(destination=output_file, format='xml')
    print(f"✅ Range triples written to {output_file}")
