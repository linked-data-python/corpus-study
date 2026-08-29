# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/test_server.py
# region: test_file_graph_data_endpoint_includes_outgoing_links_for_unrendered_targets (lines 1164-1191, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
import rdflib

@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_file_graph_data_endpoint_includes_outgoing_links_for_unrendered_targets(monkeypatch, hdf_filename):
    import h5rdmtoolbox.server as server

    graph = rdflib.Graph()
    graph.bind("ex", rdflib.Namespace("https://example.org/"))
    alpha = rdflib.URIRef("https://example.org/alpha")
    beta = rdflib.URIRef("https://example.org/beta")
    gamma = rdflib.URIRef("https://example.org/gamma")
    graph.add((alpha, rdflib.URIRef("https://example.org/name"), rdflib.Literal("Alpha")))
    graph.add((alpha, rdflib.URIRef("https://example.org/linksTo"), beta))
    graph.add((alpha, rdflib.URIRef("https://example.org/relatedTo"), gamma))
    monkeypatch.setattr(server, "get_ld", lambda *args, **kwargs: graph)
    client = TestClient(server.create_app(hdf_filename))

    response = client.get("/server_test.h5/graph-data?limit_nodes=1&limit_edges=0&include_isolated=true")
    payload = response.json()

    assert response.status_code == 200
    assert [node["id"] for node in payload["nodes"]] == [str(alpha)]
    alpha_node = payload["nodes"][0]
    assert alpha_node["literals"] == [{"predicate": "ex:name", "value": "Alpha"}]
    outgoing_links = {
        (link["predicate"], link["target_id"], link["target_label"], link["target_is_visible"])
        for link in alpha_node["outgoing_links"]
    }
    assert ("ex:linksTo", str(beta), "ex:beta", False) in outgoing_links
    assert ("ex:relatedTo", str(gamma), "ex:gamma", False) in outgoing_links
