# Extracted from cognitedata/neat@4042d3e96d : tests/v0/tests_unit/test_store/test_instance_diff.py
# region: test_diff_clears_previous_results (lines 65-93, band high)
# licence of the source repository: see meta.json
from rdflib import RDF, Literal, Namespace, URIRef
from cognite_neat_shim import NAMED_GRAPH_NAMESPACE
from cognite_neat_shim import NeatInstanceStore

def test_diff_clears_previous_results() -> None:
    """Test that calling diff twice clears previous results"""
    store = NeatInstanceStore.from_oxi_local_store()
    ex = Namespace("http://example.org/")

    current1, new1 = URIRef("urn:current1"), URIRef("urn:new1")
    current2, new2 = URIRef("urn:current2"), URIRef("urn:new2")

    # First diff
    store._add_triples([(ex.a, RDF.type, ex.T1)], named_graph=current1)
    store._add_triples([(ex.b, RDF.type, ex.T1)], named_graph=new1)
    store.diff(current1, new1)

    assert (ex.b, RDF.type, ex.T1) in store.graph(NAMED_GRAPH_NAMESPACE["DIFF_ADD"])
    assert (ex.a, RDF.type, ex.T1) in store.graph(NAMED_GRAPH_NAMESPACE["DIFF_DELETE"])

    # Second diff - should clear first results
    store._add_triples([(ex.c, RDF.type, ex.T2)], named_graph=current2)
    store._add_triples([(ex.d, RDF.type, ex.T2)], named_graph=new2)
    store.diff(current2, new2)

    add_graph = store.graph(NAMED_GRAPH_NAMESPACE["DIFF_ADD"])
    delete_graph = store.graph(NAMED_GRAPH_NAMESPACE["DIFF_DELETE"])
    assert len(add_graph) == 1
    assert len(delete_graph) == 1
    assert (ex.d, RDF.type, ex.T2) in add_graph
    assert (ex.c, RDF.type, ex.T2) in delete_graph
    assert (ex.b, RDF.type, ex.T1) not in add_graph  # Cleared
    assert (ex.a, RDF.type, ex.T1) not in delete_graph  # Cleared
