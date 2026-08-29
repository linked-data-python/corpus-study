# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/services/triple_store/adaptors/secondary/Oxigraph.py
# region: <module> (lines 583-651, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
from naas_abi_core.services.triple_store.resolve import resolve_local_http_url
from rdflib import BNode, Graph, URIRef
_DEFAULT_OXIGRAPH_URL = "http://localhost:7878"

if __name__ == "__main__":
    """
    Example usage and interactive testing for Oxigraph adapter.

    Usage:
        python Oxigraph.py
    """
    import os

    from dotenv import load_dotenv

    load_dotenv()

    oxigraph_url = resolve_local_http_url(
        "oxigraph",
        env_var="OXIGRAPH_URL",
        default_url=_DEFAULT_OXIGRAPH_URL,
    )

    print(f"Connecting to Oxigraph at {oxigraph_url}")

    try:
        adapter = Oxigraph(oxigraph_url=oxigraph_url)
        print("✓ Connected successfully")

        # Test operations
        print("\nTesting basic operations...")

        # Create test data
        test_graph_name = URIRef("http://example.org/test/graph1")
        test_graph = Graph()
        test_subject = URIRef("http://example.org/test/person1")
        test_graph.add(
            (test_subject, rdflib.RDF.type, URIRef("http://example.org/Person"))
        )
        test_graph.add(
            (
                test_subject,
                URIRef("http://example.org/name"),
                rdflib.Literal("Test Person"),
            )
        )

        # Insert
        print("- Inserting test data...")
        adapter.insert(test_graph, test_graph_name)
        print("  ✓ Insert successful")

        # Query
        print("- Querying data...")
        result = adapter.query("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
        for row in result:  # type: ignore
            print(f"  Total triples: {row.count}")  # type: ignore

        # Get subject graph
        print("- Getting subject graph...")
        subject_graph = adapter.get_subject_graph(test_subject, test_graph_name)
        print(f"  Subject has {len(subject_graph)} triples")

        # Clean up
        print("- Removing test data...")
        adapter.remove(test_graph, test_subject)
        print("  ✓ Remove successful")

        print("\n✓ All tests passed!")

    except Exception as e:  # noqa: BLE001
        print(f"✗ Error: {e}")
        print("Make sure Oxigraph is running and accessible")
