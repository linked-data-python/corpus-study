# Extracted from eccenca/cmem-plugin-shapes@52d5b16c05 : tests/test_shapes.py
# region: test_workflow_execution_add_graph_not_exists (lines 160-178, stratum remove)
# licence of the source repository: see meta.json
from cmem_client.client import Client
from cmem_plugin_base.testing import TestExecutionContext
from rdflib import DCTERMS, Graph, URIRef
from rdflib.compare import isomorphic
from cmem_plugin_shapes.plugin_shapes import (
    EXISTING_GRAPH_ADD,
    EXISTING_GRAPH_REPLACE,
    EXISTING_GRAPH_STOP,
    ShapesPlugin,
)
from tests import FIXTURE_DIR

def test_workflow_execution_add_graph_not_exists(
    graph_setup: GraphSetupFixture, client: Client
) -> None:
    """Test plugin execution with "add to graph" setting without existing graph"""
    plugin = ShapesPlugin(
        data_graph_iri=graph_setup.dataset_iri,
        shapes_graph_iri=graph_setup.shapes_iri,
        existing_graph=EXISTING_GRAPH_ADD,
        import_shapes=False,
        prefix_cc=False,
    )
    plugin.execute(inputs=[], context=TestExecutionContext(project_id=graph_setup.project_name))
    result_graph = Graph().parse(data=get_graph_content(client, graph_setup.shapes_iri))
    assert len(list(result_graph.objects(predicate=DCTERMS.created))) == 1
    assert len(list(result_graph.objects(predicate=DCTERMS.modified))) == 0
    result_graph.remove((URIRef(graph_setup.shapes_iri), DCTERMS.created, None))
    test = Graph().parse(f"{FIXTURE_DIR}/test_shapes.ttl")
    test.remove((URIRef(graph_setup.shapes_iri), DCTERMS.modified, None))
    assert isomorphic(result_graph, test)
