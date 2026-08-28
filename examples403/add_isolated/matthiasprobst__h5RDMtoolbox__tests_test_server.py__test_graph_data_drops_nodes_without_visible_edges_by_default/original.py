# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/test_server.py
# region: test_graph_data_drops_nodes_without_visible_edges_by_default (lines 1216-1241, stratum add_isolated)
# licence of the source repository: see meta.json
import pytest
import rdflib

@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
def test_graph_data_drops_nodes_without_visible_edges_by_default(monkeypatch, hdf_filename):
    import h5rdmtoolbox.server as server

    graph = rdflib.Graph()
    predicate = rdflib.URIRef("https://example.org/linksTo")
    for index in range(6):
        graph.add((
            rdflib.URIRef(f"https://example.org/node-{index}"),
            predicate,
            rdflib.URIRef(f"https://example.org/node-{index + 1}"),
        ))
    monkeypatch.setattr(server, "get_ld", lambda *args, **kwargs: graph)
    client = TestClient(server.create_app(hdf_filename))

    response = client.get("/server_test.h5/graph-data?limit_nodes=5&limit_edges=1")
    payload = response.json()

    assert response.status_code == 200
    assert payload["summary"]["shown_edges"] == 1
    assert payload["summary"]["shown_nodes"] == 2
    assert payload["summary"]["dropped_isolated_visible_nodes"] == 3
    visible_ids = {node["id"] for node in payload["nodes"]}
    for edge in payload["edges"]:
        assert edge["from"] in visible_ids
        assert edge["to"] in visible_ids
