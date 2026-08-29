# Extracted from ArangoDB-Community/ArangoRDF@48cfed903a : tests/test_main.py
# region: test_rpt_case_11_2 (lines 888-944, stratum trav_one_step)
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
    [("Case_11_2_RPT", get_rdf_graph("cases/11_2.ttl"))],
)
def test_rpt_case_11_2(name: str, rdf_graph: RDFGraph) -> None:
    NUM_TRIPLES = 3
    NUM_URIREFS = 3
    NUM_BNODES = 0
    NUM_LITERALS = 1

    alice = URIRef("http://example.com/alice")
    friend = URIRef("http://example.com/friend")
    bob = URIRef("http://example.com/bob")
    mentionedby = URIRef("http://example.com/mentionedBy")
    alex = URIRef("http://example.com/alex")
    age = URIRef("http://example.com/age")

    _alice = adbrdf.rdf_id_to_adb_key(str(alice))
    _bob = adbrdf.rdf_id_to_adb_key(str(bob))
    _mentionedby = adbrdf.rdf_id_to_adb_key(str(mentionedby))
    _alex = adbrdf.rdf_id_to_adb_key(str(alex))
    _age = adbrdf.rdf_id_to_adb_key(str(age))
    _25 = adbrdf.rdf_id_to_adb_key("25")
    _alice_friend_bob = adbrdf.rdf_id_to_adb_key(
        str(rdf_graph.value(predicate=RDF.type, object=RDF.Statement))
    )

    adb_graph = adbrdf.rdf_to_arangodb_by_rpt(
        name,
        rdf_graph + RDFGraph(),
        overwrite_graph=True,
    )

    URIREF_COL = adb_graph.vertex_collection(f"{name}_URIRef")
    assert URIREF_COL.has(_alice)
    assert URIREF_COL.has(_bob)
    assert URIREF_COL.has(_alex)

    STATEMENT_COL = adb_graph.edge_collection(f"{name}_Statement")
    assert STATEMENT_COL.has(_alice_friend_bob)
    assert STATEMENT_COL.has(adbrdf.hash(f"{_alex}-{_age}-{_25}"))
    assert STATEMENT_COL.has(adbrdf.hash(f"{_alice_friend_bob}-{_mentionedby}-{_alex}"))

    v_count, e_count = get_adb_graph_count(name)
    assert v_count == NUM_URIREFS + NUM_BNODES + NUM_LITERALS
    assert e_count == NUM_TRIPLES

    rdf_graph_2 = adbrdf.arangodb_graph_to_rdf(name, type(rdf_graph)())

    statement = rdf_graph_2.value(predicate=RDF.type, object=RDF.Statement)
    assert (statement, RDF.subject, alice) in rdf_graph_2
    assert (statement, RDF.predicate, friend) in rdf_graph_2
    assert (statement, RDF.object, bob) in rdf_graph_2
    assert (statement, mentionedby, alex) in rdf_graph_2
    assert len(rdf_graph_2) == len(rdf_graph)

    db.delete_graph(name, drop_collections=True)
