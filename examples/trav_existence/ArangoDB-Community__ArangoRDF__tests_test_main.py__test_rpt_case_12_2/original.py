# Extracted from ArangoDB-Community/ArangoRDF@48cfed903a : tests/test_main.py
# region: test_rpt_case_12_2 (lines 1003-1054, stratum trav_existence)
# licence of the source repository: see meta.json
import pytest
from rdflib import RDF, RDFS, BNode
from rdflib import Graph as RDFGraph
from rdflib import Literal, Namespace, URIRef
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

@pytest.mark.parametrize(
    "name, rdf_graph",
    [("Case_12_2_RPT", get_rdf_graph("cases/12_2.ttl"))],
)
def test_rpt_case_12_2(name: str, rdf_graph: RDFGraph) -> None:
    NUM_TRIPLES = 2
    NUM_URIREFS = 3
    NUM_BNODES = 0
    NUM_LITERALS = 0

    lara = URIRef("http://example.com/lara")
    writer = URIRef("http://example.com/writer")
    owner = URIRef("http://example.com/owner")
    journal = URIRef("http://example.com/journal")

    _lara = adbrdf.rdf_id_to_adb_key(str(lara))
    _writer = adbrdf.rdf_id_to_adb_key(str(writer))
    _owner = adbrdf.rdf_id_to_adb_key(str(owner))
    _journal = adbrdf.rdf_id_to_adb_key(str(journal))
    _lara_type_writer = adbrdf.rdf_id_to_adb_key(
        str(rdf_graph.value(predicate=RDF.type, object=RDF.Statement))
    )

    adb_graph = adbrdf.rdf_to_arangodb_by_rpt(
        name,
        rdf_graph + RDFGraph(),
        overwrite_graph=True,
    )

    URIREF_COL = adb_graph.vertex_collection(f"{name}_URIRef")
    assert URIREF_COL.has(_lara)
    assert URIREF_COL.has(_writer)
    assert URIREF_COL.has(_journal)

    STATEMENT_COL = adb_graph.edge_collection(f"{name}_Statement")
    assert STATEMENT_COL.has(_lara_type_writer)
    assert STATEMENT_COL.has(adbrdf.hash(f"{_lara_type_writer}-{_owner}-{_journal}"))

    v_count, e_count = get_adb_graph_count(name)
    assert v_count == NUM_URIREFS + NUM_BNODES + NUM_LITERALS
    assert e_count == NUM_TRIPLES

    rdf_graph_2 = adbrdf.arangodb_graph_to_rdf(name, type(rdf_graph)())

    statement = rdf_graph_2.value(predicate=RDF.type, object=RDF.Statement)
    assert (statement, RDF.subject, lara) in rdf_graph_2
    assert (statement, RDF.predicate, RDF.type) in rdf_graph_2
    assert (statement, RDF.object, writer) in rdf_graph_2
    assert (statement, owner, journal) in rdf_graph_2
    assert len(rdf_graph_2) == len(rdf_graph)

    db.delete_graph(name, drop_collections=True)
