# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_interop_foundation.py
# region: test_registry_chain_covers_all_apps_every_registration_a_container_tree (lines 59-82, stratum trav_existence)
# licence of the source repository: see meta.json
#
# The extracted region built its graph from a real file on disk (REG /
# REPO, one of the corpus/403 "163 regions with no visible graph" -- see
# AGENT_BATCH.md): `REPO` is undefined outside the source checkout, so the
# region cannot even be imported as extracted. Restored the binding as an
# explicit `graph` parameter (see meta.json) and dropped the now-unused
# REG/parse line; `g = graph` is the one line left in its place.
import rdflib
TREE_NS = "https://pod.vardeman.me/vault/meta/shapetrees/wiki-memory.tree#"
INTEROP = rdflib.Namespace("http://www.w3.org/ns/solid/interop#")
OWNER = rdflib.URIRef("https://pod.vardeman.me/vault/profile/card#me")
ABTREE_NS = "https://pod.vardeman.me/vault/meta/shapetrees/addressbook.tree#"
IDTREE_NS = "https://pod.vardeman.me/vault/meta/shapetrees/id-schemes.tree#"

def test_registry_chain_covers_all_apps_every_registration_a_container_tree(graph):
    g = graph
    rset = g.value(OWNER, INTEROP.hasRegistrySet)
    assert rset is not None, "owner WebID has no hasRegistrySet"
    dreg = g.value(rset, INTEROP.hasDataRegistry)
    assert dreg is not None, "RegistrySet has no DataRegistry"
    regs = list(g.objects(dreg, INTEROP.hasDataRegistration))
    assert len(regs) == 12, f"expected 12 DataRegistrations, got {len(regs)}"
    for r in regs:
        t = g.value(r, INTEROP.registeredShapeTree)
        assert t is not None and str(t).endswith("ContainerTree"), \
            f"{r}: registeredShapeTree must be a ContainerTree, got {t}"
    REG_NS = rdflib.Namespace("https://pod.vardeman.me/vault/meta/interop/registry#")
    wiki = [r for r in regs if r not in (REG_NS["id-schemes"], REG_NS["contacts-person"], REG_NS["contacts-organization"], REG_NS["contacts-group"], REG_NS["contacts-membership"])]
    assert len(wiki) == 7, f"expected 7 wiki-memory registrations, got {len(wiki)}"
    for r in wiki:
        assert str(g.value(r, INTEROP.registeredShapeTree)).startswith(TREE_NS), \
            f"{r}: wiki registration must point into wiki-memory.tree"
    assert g.value(REG_NS["contacts-person"], INTEROP.registeredShapeTree) == rdflib.URIRef(ABTREE_NS + "PersonContainerTree")
    assert g.value(REG_NS["contacts-organization"], INTEROP.registeredShapeTree) == rdflib.URIRef(ABTREE_NS + "OrganizationContainerTree")
    assert g.value(REG_NS["contacts-group"], INTEROP.registeredShapeTree) == rdflib.URIRef(ABTREE_NS + "GroupContainerTree")
    assert g.value(REG_NS["contacts-membership"], INTEROP.registeredShapeTree) == rdflib.URIRef(ABTREE_NS + "MembershipContainerTree")
    assert g.value(REG_NS["id-schemes"], INTEROP.registeredShapeTree) == \
        rdflib.URIRef(IDTREE_NS + "SchemeRecordContainerTree")
