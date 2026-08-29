# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_addressbook_floor_parity.py
# region: _tree_shapes_by_container (lines 21-36, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
ST = Namespace("http://www.w3.org/ns/shapetrees#")
TREE = REPO / "overlays/addressbook/shapetrees/addressbook.tree.ttl"
MGR_DIR = REPO / "overlays/addressbook/interop/managers"

def _tree_shapes_by_container() -> dict:
    "managed-container-url -> {st:shape IRIs reachable via Manager->ContainerTree->contains}."
    tg = Graph(); tg.parse(TREE, format="turtle")
    out = {}
    for mf in MGR_DIR.glob("*.shapetree.ttl"):
        mg = Graph(); mg.parse(mf, format="turtle")
        for a in mg.objects(None, ST.hasAssignment):
            ctr = mg.value(a, ST.manages); tree = mg.value(a, ST.assigns)
            if ctr is None or tree is None:
                continue
            shapes = set()
            for res_tree in tg.objects(URIRef(str(tree)), ST.contains):
                for sh in tg.objects(res_tree, ST.shape):
                    shapes.add(str(sh))
            out[str(ctr)] = shapes
    return out
