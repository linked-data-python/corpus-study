# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/integration/test_l4_extension_overlay.py
# region: _n3_patch_delete_ti_registration (lines 49-74, stratum ns_def_local)
# licence of the source repository: see meta.json
import httpx
from tests.conftest import _pod_base, resolve_ca as _resolve_ca
_TI_URL = POD + "/settings/publicTypeIndex"
_REG_IRI = _TI_URL + "#reg0-test-biz-overlay"

def _n3_patch_delete_ti_registration(client: httpx.Client) -> None:
    """N3-Patch-DELETE the biz-overlay Type-Index registration triples.

    Mirrors what apply.py does with solid:inserts but uses solid:deletes.
    Reads the current TI to find the exact triples, then removes them.
    """
    # Build the three triples to remove as N-Triples (rdflib canonical form)
    from rdflib import Graph, URIRef, RDF, Namespace
    SOLID_NS = Namespace("http://www.w3.org/ns/solid/terms#")
    reg = URIRef(_REG_IRI)
    g = Graph()
    g.add((reg, RDF.type, SOLID_NS.TypeRegistration))
    g.add((reg, SOLID_NS.forClass, URIRef("https://chuck.example/biz/Equipment")))
    g.add((reg, SOLID_NS.instanceContainer, URIRef(_pod_base() + "/biz/equipment/")))
    ntriples = g.serialize(format="nt").strip()
    if not ntriples:
        return
    patch_body = (
        "@prefix solid: <http://www.w3.org/ns/solid/terms#>.\n\n"
        f"_:patch a solid:InsertDeletePatch ;\n"
        f"   solid:deletes {{ {ntriples} }} .\n"
    )
    r = client.patch(_TI_URL, content=patch_body.encode("utf-8"),
                     headers={"Content-Type": "text/n3"})
    if r.status_code not in (200, 204, 205):
        print(f"  [teardown] PATCH-DELETE TI registration → {r.status_code} {r.text[:120]}")
