# Extracted from aigora-de/rdf-construct@670e400ea4 : tests/test_diff.py
# region: TestCompareGraphs.test_hierarchy_change (lines 122-142, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from rdflib.namespace import OWL, XSD
from rdf_construct.diff import (
    compare_graphs,
    filter_diff,
    parse_filter_string,
    ChangeType,
    EntityChange,
    EntityType,
    GraphDiff,
    TripleChange,
    PredicateCategory,
)
EX = Namespace("http://example.org/")

def test_hierarchy_change(self):
    """Detect a change in class hierarchy."""
    g1 = Graph()
    g1.add((EX.ClassA, RDF.type, OWL.Class))
    g1.add((EX.ClassA, RDFS.subClassOf, EX.Thing))

    g2 = Graph()
    g2.add((EX.ClassA, RDF.type, OWL.Class))
    g2.add((EX.ClassA, RDFS.subClassOf, EX.PhysicalEntity))  # New parent

    diff = compare_graphs(g1, g2)

    assert not diff.is_identical
    assert len(diff.modified) == 1

    modified = diff.modified[0]
    # Should have removed old subClassOf and added new one
    added_preds = [t.predicate for t in modified.added_triples]
    removed_preds = [t.predicate for t in modified.removed_triples]
    assert RDFS.subClassOf in added_preds
    assert RDFS.subClassOf in removed_preds
