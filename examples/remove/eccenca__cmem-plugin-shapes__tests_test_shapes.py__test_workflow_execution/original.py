# Extracted from eccenca/cmem-plugin-shapes@52d5b16c05 : tests/test_shapes.py
# region: test_workflow_execution (lines 126-157, stratum remove)
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

def test_workflow_execution(graph_setup: GraphSetupFixture, client: Client) -> None:
    """Test plugin execution"""
    plugin = ShapesPlugin(
        data_graph_iri=graph_setup.dataset_iri,
        shapes_graph_iri=graph_setup.shapes_iri,
        existing_graph=EXISTING_GRAPH_REPLACE,
        import_shapes=False,
        prefix_cc=False,
        plugin_provenance=True,
    )
    plugin.execute(inputs=[], context=TestExecutionContext(project_id=graph_setup.project_name))
    result_graph_content = get_graph_content(client, graph_setup.shapes_iri)
    regexp = rf"<{graph_setup.shapes_iri}> <http://purl.org/dc/terms/created> .* \."
    created = re.findall(regexp, result_graph_content)
    assert len(created) == 1
    datetime = created[0].split()[-2]
    assert DATETIME_PATTERN.match(datetime)
    result_graph = Graph().parse(data=result_graph_content)
    assert len(list(result_graph.objects(predicate=DCTERMS.modified))) == 0
    result_graph.remove((URIRef(graph_setup.shapes_iri), DCTERMS.created, None))
    test = Graph().parse(f"{FIXTURE_DIR}/test_shapes.ttl")
    assert isomorphic(result_graph, test)
    with pytest.raises(
        ValueError, match=r"Graph <http://docker.localhost/my-persons-shapes> already exists."
    ):
        ShapesPlugin(
            data_graph_iri=graph_setup.dataset_iri,
            shapes_graph_iri=graph_setup.shapes_iri,
            existing_graph=EXISTING_GRAPH_STOP,
            import_shapes=False,
            prefix_cc=False,
        ).execute(inputs=[], context=TestExecutionContext(project_id=graph_setup.project_name))
