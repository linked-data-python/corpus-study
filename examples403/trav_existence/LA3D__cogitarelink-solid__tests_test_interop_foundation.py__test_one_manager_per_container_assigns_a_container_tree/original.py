# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_interop_foundation.py
# region: test_one_manager_per_container_assigns_a_container_tree (lines 108-120, stratum trav_existence)
# licence of the source repository: see meta.json
#
# The extracted region built its own graph per slug from a real file on disk
# (MGR_DIR / REPO, one of the corpus/403 "163 regions with no visible graph"
# -- see AGENT_BATCH.md): `REPO` is undefined outside the source checkout, so
# the region cannot even be imported as extracted. Restored the binding as
# an explicit `graph` parameter (see meta.json) and dropped the now-unused
# MGR_DIR/file-existence/parse lines; `g = graph` is the one line left in
# their place, so the per-slug body is otherwise untouched.
import rdflib
ST = rdflib.Namespace("http://www.w3.org/ns/shapetrees#")
CONTAINER_SLUGS = ["concepts", "people", "places", "events", "organizations", "procedures", "working"]

def test_one_manager_per_container_assigns_a_container_tree(graph):
    for slug in CONTAINER_SLUGS:
        g = graph
        mgr = next(g.subjects(rdflib.RDF.type, ST.Manager))
        a = g.value(mgr, ST.hasAssignment)
        assert a is not None, f"{slug}: no st:hasAssignment"
        assigned = g.value(a, ST.assigns)
        assert assigned is not None and str(assigned).endswith("ContainerTree"), f"{slug}: st:assigns must be a ContainerTree"
        # A container Manager assigns the container tree + names the managed container; the per-resource
        # validation focus is each contained resource's <#this> (resolved at validation, not pinned here).
        assert g.value(a, ST.manages) is not None, f"{slug}: st:manages must name the container"
