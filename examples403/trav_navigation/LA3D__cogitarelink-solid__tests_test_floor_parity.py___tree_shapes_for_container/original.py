# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_floor_parity.py
# region: _tree_shapes_for_container (lines 71-89, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef
ST   = Namespace("http://www.w3.org/ns/shapetrees#")
TREE_DOC   = OVERLAY / "shapetrees" / "wiki-memory.tree.ttl"
MANAGERS   = OVERLAY / "interop" / "managers"
TREE_BASE  = "https://pod.vardeman.me/vault/meta/shapetrees/wiki-memory.tree"

def _tree_shapes_for_container() -> dict[str, set[str]]:
    """container-path -> {shape IRIs reachable via Manager -> ContainerTree -> st:contains -> st:shape}."""
    tg = Graph(); tg.parse(TREE_DOC, format="turtle", publicID=TREE_BASE)
    out: dict[str, set[str]] = {}
    for mf in MANAGERS.glob("*.shapetree.ttl"):
        mg = Graph(); mg.parse(mf, format="turtle")
        for assignment in mg.objects(None, ST.hasAssignment):
            ctr  = mg.value(assignment, ST.manages)
            tree = mg.value(assignment, ST.assigns)
            if ctr is None or tree is None:
                continue
            shapes: set[str] = set()
            for res_tree in tg.objects(URIRef(str(tree)), ST.contains):
                # Task 8: a ResourceTree may carry MULTIPLE st:shape (Page+Thing+leaf);
                # collect them all (tg.value would return only one).
                for sh in tg.objects(res_tree, ST.shape):
                    shapes.add(str(sh))
            out[str(ctr)] = shapes
    return out
