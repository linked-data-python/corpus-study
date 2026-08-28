# Extracted from LA3D/cogitarelink-solid@49121503ea : scripts/overlay/common.py
# region: parse_manifest (lines 217-222, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
OVERLAY = Namespace("https://pod.vardeman.me/vault/ontology/overlay#")

for v_node in many(OVERLAY.declaresVocabulary):
    ns = next(g.objects(v_node, OVERLAY.namespace), None)
    doc = next(g.objects(v_node, OVERLAY.document), None)
    host = next(g.objects(v_node, OVERLAY.hostedAt), None)
    if ns and doc and host:
        vocabs.append(VocabularyDeclaration(URIRef(ns), overlay_dir / str(doc), str(host)))
