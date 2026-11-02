# Extracted from statnett/KGraphPy@38859be62f : tests/test_graph.py
# region: test_iadd (lines 131-144, stratum add_isolated)
# licence of the source repository: see meta.json
import context_shim
from rdflib import URIRef, Literal, Namespace
from kgraphpy.processor import CIMProcessor
from kgraphpy.graph import CIMGraph

def test_iadd() -> None:
    g = CIMGraph(identifier=URIRef("self_graph"))
    pr = CIMProcessor(g, provenance_description="Initial load")
    otherg = CIMGraph(identifier=URIRef("other_graph"))
    otherg.add((URIRef("s1"), URIRef("p1"), Literal("o")))
    g += otherg

    assert (URIRef("s1"), URIRef("p1"), Literal("o")) in pr.graph
    assert pr.provenance and pr._provenance
    entries = pr.provenance.entries
    assert len(entries) == 2
    assert entries[1]["step_name"] == "merging_graphs"
    assert entries[1]["description"] == "Graph other_graph merged into self_graph."
    assert pr._provenance._entries[1].sub_steps == []   # addN is used instead of g.add when merging, so no substeps should be recorded
