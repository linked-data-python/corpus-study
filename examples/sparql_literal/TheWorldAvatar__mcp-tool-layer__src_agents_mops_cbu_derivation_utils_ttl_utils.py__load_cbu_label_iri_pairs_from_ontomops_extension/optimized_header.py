# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/agents/mops/cbu_derivation/utils/ttl_utils.py
# region: load_cbu_label_iri_pairs_from_ontomops_extension (lines 78-113, stratum sparql_literal)
# licence of the source repository: see meta.json
import os
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS
from ttl_utils_shim import load_graph_from_file  # context shim, see meta.json

def load_cbu_label_iri_pairs_from_ontomops_extension(hash_value: str) -> list[tuple[str, str]]:
    """Return list of (label, iri) for all ontomops:ChemicalBuildingUnit individuals."""
    from models.locations import DATA_DIR
    g = load_graph_from_file(os.path.join(DATA_DIR, hash_value, "ontomops_extension.ttl"))
    ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")
    g.bind("ontomops", ONTOMOPS)
    # Deduplicate by label keeping first seen
    pairs: dict[str, str] = {}
    try:
        for s, label in g.query(
            "SELECT ?s ?label WHERE { ?s a ontomops:ChemicalBuildingUnit ; rdfs:label ?label }"
        ):
            if str(label) and str(s):
                pairs.setdefault(str(label), str(s))
    except Exception:
        for s in g.subjects(RDF.type, ONTOMOPS.ChemicalBuildingUnit):
            for o in g.objects(s, RDFS.label):
                if str(o):
                    pairs.setdefault(str(o), str(s))
    return list(pairs.items())
