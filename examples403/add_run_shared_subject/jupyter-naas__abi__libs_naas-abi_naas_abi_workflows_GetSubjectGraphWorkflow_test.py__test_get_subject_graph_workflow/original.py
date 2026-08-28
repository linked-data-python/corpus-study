# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi/naas_abi/workflows/GetSubjectGraphWorkflow_test.py
# region: test_get_subject_graph_workflow (lines 27-76, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from naas_abi.workflows.GetSubjectGraphWorkflow import (
    GetSubjectGraphWorkflow,
    GetSubjectGraphWorkflowConfiguration,
    GetSubjectGraphWorkflowParameters,
)
triple_store_service = ABIModule.get_instance().engine.services.triple_store

def test_get_subject_graph_workflow(
    get_subject_graph_workflow: GetSubjectGraphWorkflow,
):
    from uuid import uuid4

    from naas_abi_core import logger
    from naas_abi_core.utils.Graph import TEST
    from rdflib import OWL, RDFS, Graph, Literal, URIRef

    graph = Graph()
    node_id = str(uuid4())
    uri = TEST[node_id]
    logger.debug(f"Creating graph with URI: {uri}")
    graph.add(
        (
            uri,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("https://www.commoncoreontologies.org/ont00000443"),
        )
    )
    graph.add(
        (
            uri,
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            OWL.NamedIndividual,
        )
    )
    graph.add((uri, RDFS.label, Literal(node_id)))

    triple_store_service.insert(graph)

    result = get_subject_graph_workflow.get_subject_graph(
        GetSubjectGraphWorkflowParameters(
            uri=str(uri),
        )
    )

    assert isinstance(result, str), result
    assert result != "", result

    triple_store_service.remove(graph)

    # Test
    result = get_subject_graph_workflow.get_subject_graph(
        GetSubjectGraphWorkflowParameters(
            uri=str(uri),
        )
    )

    assert isinstance(result, str), result
