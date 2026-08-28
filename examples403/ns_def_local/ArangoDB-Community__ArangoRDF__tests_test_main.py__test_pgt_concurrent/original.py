# Extracted from ArangoDB-Community/ArangoRDF@48cfed903a : tests/test_main.py
# region: test_pgt_concurrent (lines 5655-5698, stratum ns_def_local)
# licence of the source repository: see meta.json
from concurrent.futures import ThreadPoolExecutor, as_completed
from rdflib import Graph as RDFGraph
from rdflib import Literal, Namespace, URIRef
from arango_rdf import ArangoRDF
from .conftest import (
    adbrdf,
    arango_restore,
    db,
    get_adb_graph_count,
    get_bnodes,
    get_literal_statements,
    get_literals,
    get_meta_graph,
    get_rdf_graph,
    get_uris,
    subtract_graphs,
)

def test_pgt_concurrent() -> None:
    db.delete_graph("Test", drop_collections=True, ignore_missing=True)

    EX = Namespace("http://example.org/")

    g1 = RDFGraph()
    g1.add((EX.Alice, EX.knows, EX.Bob))
    g1.add((EX.Alice, EX.name, Literal("Alice")))

    g2 = RDFGraph()
    g2.add((EX.Bob, EX.knows, EX.Charlie))
    g2.add((EX.Bob, EX.name, Literal("Bob")))

    graph_specs = [("Test", g1), ("Test", g2)]
    results = []

    def import_rdf(graph_name: str, rdf_graph: RDFGraph) -> str:
        # Disable rich progress bars to avoid interference with concurrent modules
        adbrdf = ArangoRDF(db, enable_rich=False)
        adbrdf.rdf_to_arangodb_by_pgt(
            graph_name,
            rdf_graph,
            overwrite_graph=False,
            # Triple Reification is **not** thread-safe due to SPARQL queries
            flatten_reified_triples=False,
            resource_collection_name="Node",
            # For concurrent inserts: ignore duplicates, don't raise on conflicts
            overwrite_mode="ignore",
            raise_on_document_error=False,
        )

        return graph_name

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(import_rdf, name, graph) for name, graph in graph_specs
        ]
        for future in as_completed(futures):
            results.append(future.result())

    assert db.has_graph("Test")
    assert db.collection("Node").count() == 3
    assert db.collection("Property").count() == 2
    assert db.collection("knows").count() == 2
