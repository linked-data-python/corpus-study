# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/pipelines/utils/ttl_publisher.py
# region: _prune_thorax_checklist_without_ops_code_in_graph (lines 485-499, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
_MED = "https://www.theworldavatar.com/kg/medical/"
_OPS_CODES_TTL_RE = re.compile(r"8[-_]?\s*144\.0|5[-_]?\s*340\.0", re.IGNORECASE)

def _prune_thorax_checklist_without_ops_code_in_graph(g: Graph) -> None:
    """
    Drop Thoraxdrainageneinlage checklist triples when no explicit OPS coding
    appears anywhere in the merged RDF. Matches structured GT that codes only OPS rows,
    not narrative drainage mentions.
    """
    pred = URIRef(f"{_MED}Thoraxdrainageneinlage_8_144_0_und_5_340_0")
    try:
        blob = g.serialize(format="turtle")
    except Exception:
        return
    if _OPS_CODES_TTL_RE.search(blob):
        return
    for s, p, o in list(g.triples((None, pred, None))):
        g.remove((s, p, o))
