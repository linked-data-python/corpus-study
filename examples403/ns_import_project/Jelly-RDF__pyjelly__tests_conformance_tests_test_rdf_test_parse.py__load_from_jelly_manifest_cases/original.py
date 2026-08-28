# Extracted from Jelly-RDF/pyjelly@cf762d1cfe : tests/conformance_tests/test_rdf/test_parse.py
# region: load_from_jelly_manifest_cases (lines 51-102, stratum ns_import_project)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import Dataset, Graph, Node, URIRef
from rdflib.namespace import RDF
from tests.conformance_tests.test_rdf._common import (
    JELLYT,
    MF,
    categorize_by_requires,
)

def load_from_jelly_manifest_cases(manifest_path: Path) -> list[FromJellyTestCase]:
    if not manifest_path.exists():
        return []
    graph = Graph()
    graph.parse(manifest_path, format="turtle")
    manifest_dir = manifest_path.parent
    base_uri_from_manifest = "https://w3id.org/jelly/dev/tests/rdf/from_jelly/"
    test_cases = []
    test_type_map = {
        JELLYT.TestPositive: "positive",
        JELLYT.TestNegative: "negative",
    }
    for test_class, test_type_str in test_type_map.items():
        for test_uri in graph.subjects(RDF.type, test_class):
            if not isinstance(test_uri, URIRef):
                continue
            # Map MF.action to the actual input file path
            action_uri = graph.value(test_uri, MF.action)
            action_rel_path = str(action_uri).replace(base_uri_from_manifest, "")
            action_path = manifest_dir / action_rel_path

            # MF.result can be a single file or an RDF list of files
            result_paths = None
            result_node = graph.value(test_uri, MF.result)
            if result_node:
                if (result_node, RDF.first, None) in graph:
                    # Handle list of result files
                    result_uris = graph.items(result_node)
                    result_paths = [
                        manifest_dir / str(uri).replace(base_uri_from_manifest, "")
                        for uri in result_uris
                    ]
                else:
                    # Single result file
                    result_rel_path = str(result_node).replace(
                        base_uri_from_manifest, ""
                    )
                    result_paths = [manifest_dir / result_rel_path]

            # Each test case knows its category (rdf11/generalized/etc.)
            # from categorize_by_requires
            test_cases.append(
                FromJellyTestCase(
                    uri=str(test_uri),
                    name=str(graph.value(test_uri, MF.name) or ""),
                    action_path=action_path,
                    result_paths=result_paths,
                    test_type=test_type_str,
                    category=categorize_by_requires(graph, test_uri),
                )
            )
    return test_cases
