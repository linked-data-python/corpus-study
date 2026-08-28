# Extracted from Jelly-RDF/pyjelly@cf762d1cfe : tests/conformance_tests/test_rdf/test_serialize.py
# region: _process_test_case (lines 83-105, stratum trav_single_value)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import Graph, Node, URIRef
from tests.conformance_tests.test_rdf._common import (
    JELLYT,
    MF,
    categorize_by_requires,
)

def _process_test_case(
    graph: Graph,
    test_uri: URIRef,
    manifest_dir: Path,
    base_uri: str,
    test_type_str: str,
) -> ToJellyTestCase | None:
    action_node = graph.value(test_uri, MF.action)
    action_paths, options_path = _process_action_node(
        graph, action_node, manifest_dir, base_uri
    )

    result_path = _process_result_node(graph, test_uri, manifest_dir, base_uri)

    return ToJellyTestCase(
        uri=str(test_uri),
        name=str(graph.value(test_uri, MF.name) or ""),
        action_paths=action_paths,
        options_path=options_path,
        result_path=result_path,
        test_type=test_type_str,
        category=categorize_by_requires(graph, test_uri),
    )
