# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/agents/mops/cbu_derivation/utils/ttl_utils.py
# region: load_cbu_label_iri_pairs_from_ontomops_extension (lines 78-113, stratum sparql_literal)
# licence of the source repository: see meta.json
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

def load_cbu_label_iri_pairs_from_ontomops_extension(hash_value: str) -> list[tuple[str, str]]:
    """Return list of (label, iri) for all ontomops:ChemicalBuildingUnit individuals."""
    from models.locations import DATA_DIR
    path = os.path.join(DATA_DIR, hash_value, "ontomops_extension.ttl")
    g = load_graph_from_file(path)
    ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")
    g.bind("ontomops", ONTOMOPS)
    pairs: list[tuple[str, str]] = []
    try:
        q = (
            """
            SELECT DISTINCT ?s ?label WHERE {
              ?s a ontomops:ChemicalBuildingUnit ; rdfs:label ?label .
            }
            """
        )
        for row in g.query(q, initNs={"ontomops": ONTOMOPS, "rdfs": RDFS}):
            iri = str(row[0])
            lbl = str(row[1])
            if lbl and iri:
                pairs.append((lbl, iri))
    except Exception:
        for s in g.subjects(RDF.type, ONTOMOPS.ChemicalBuildingUnit):
            iri = str(s)
            for o in g.objects(s, RDFS.label):
                lbl = str(o)
                if lbl:
                    pairs.append((lbl, iri))
    # Deduplicate by label keeping first seen
    seen = set()
    out: list[tuple[str, str]] = []
    for lbl, iri in pairs:
        if lbl not in seen:
            seen.add(lbl)
            out.append((lbl, iri))
    return out
