# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/metadata/test_extensions.py
# region: test_page_honours_limit_and_offset (lines 366-384, stratum trav_one_step)
# licence of the source repository: see meta.json
import pytest
from fastapi.testclient import TestClient
from rdflib import Graph, Literal, URIRef
BASE_URL = "http://localhost:8000"
DCAT_CATALOG = "http://www.w3.org/ns/dcat#catalog"

@pytest.mark.unit
def test_page_honours_limit_and_offset() -> None:
    repo = _repo_with_catalogs(10)
    app = _build_app(repo=repo, pdp=_FakePDP(), cache=_two_level_cache())
    response = TestClient(app).get("/page/catalog?limit=3&offset=4")
    assert response.status_code == 200
    g = Graph()
    g.parse(data=response.text, format="turtle")
    children = sorted(str(o) for o in g.objects(URIRef(BASE_URL), URIRef(DCAT_CATALOG)))
    # We asked for 3 starting at offset 4. Catalogs are sorted by IRI,
    # so c-04, c-05, c-06.
    assert children == [
        f"{BASE_URL}/catalog/c-04",
        f"{BASE_URL}/catalog/c-05",
        f"{BASE_URL}/catalog/c-06",
    ]
    assert response.headers["X-FDP-Page-Total"] == "10"
    assert response.headers["X-FDP-Page-Offset"] == "4"
    assert response.headers["X-FDP-Page-Limit"] == "3"
