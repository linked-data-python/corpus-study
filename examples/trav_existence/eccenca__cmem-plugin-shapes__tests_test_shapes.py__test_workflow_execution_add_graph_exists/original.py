# Extracted from eccenca/cmem-plugin-shapes@52d5b16c05 : tests/test_shapes.py
# region: test_workflow_execution_add_graph_exists (lines 181-210, stratum trav_existence)
# licence of the source repository: see meta.json
import re
import pytest
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
DATETIME_PATTERN = re.compile(
    r'^"[1-9][0-9]{3}-(0[1-9]|1[0-2])-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9].[0-9]{3}Z"\^\^'
    "<http://www.w3.org/2001/XMLSchema#dateTime>"
)

@pytest.mark.parametrize("add_to_graph", [True])
def test_workflow_execution_add_graph_exists(
    graph_setup: GraphSetupFixture, add_to_graph: bool, client: Client
) -> None:
    """Test plugin execution with "add to graph" setting with existing graph"""
    plugin = ShapesPlugin(
        data_graph_iri=graph_setup.dataset_iri,
        shapes_graph_iri=graph_setup.shapes_iri,
        existing_graph=EXISTING_GRAPH_ADD,
        import_shapes=False,
        prefix_cc=False,
        label="New label",
    )
    assert graph_setup.add_to_graph == add_to_graph
    plugin.execute(inputs=[], context=TestExecutionContext(project_id=graph_setup.project_name))
    result_graph_content = get_graph_content(client, graph_setup.shapes_iri)
    regexp = rf"<{graph_setup.shapes_iri}> <http://purl.org/dc/terms/modified> .* \."
    modified = re.findall(regexp, result_graph_content)
    assert len(modified) == 1
    datetime = modified[0].split()[-2]
    assert DATETIME_PATTERN.match(datetime)
    result_graph = Graph().parse(data=result_graph_content)
    test = Graph().parse(f"{FIXTURE_DIR}/test_shapes_add.ttl")
    assert result_graph.value(
        subject=URIRef(graph_setup.shapes_iri), predicate=DCTERMS.modified
    ) != test.value(subject=URIRef(graph_setup.shapes_iri), predicate=DCTERMS.modified)
    assert len(list(result_graph.objects(predicate=DCTERMS.created))) == 0
    result_graph.remove((URIRef(graph_setup.shapes_iri), DCTERMS.modified, None))
    test.remove((URIRef(graph_setup.shapes_iri), DCTERMS.modified, None))
    assert isomorphic(result_graph, test)
