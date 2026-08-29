# Extracted from vemonet/rdflib-endpoint@1427c77829 : tests/test_rdflib_endpoint.py
# region: test_service_description (lines 69-86, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import RDFS, Graph, Literal, URIRef, Variable
from rdflib_endpoint.sparql_router import SD
endpoint = TestClient(app)

def test_service_description():
    # Check GET turtle
    response = endpoint.get("/", headers={"accept": "text/turtle"})
    assert response.status_code == 200
    g = Graph()
    g.parse(data=response.text, format="turtle")
    assert any(g.triples((None, SD.endpoint, None))), "Missing sd:endpoint in service description"
    assert any(g.triples((None, SD.extensionFunction, None))), "Missing sd:extensionFunction in service description"
    assert len(list(g.triples((None, SD.extensionFunction, None)))) >= 1, "Expected at least 1 extension function"

    # Check POST XML
    response = endpoint.post("/", headers={"accept": "application/xml"})
    assert response.status_code == 200
    g = Graph()
    g.parse(data=response.text, format="xml")
    assert any(g.triples((None, SD.endpoint, None))), "Missing sd:endpoint in service description"
    assert any(g.triples((None, SD.extensionFunction, None))), "Missing sd:extensionFunction in service description"
    assert len(list(g.triples((None, SD.extensionFunction, None)))) >= 1, "Expected at least 1 extension function"
