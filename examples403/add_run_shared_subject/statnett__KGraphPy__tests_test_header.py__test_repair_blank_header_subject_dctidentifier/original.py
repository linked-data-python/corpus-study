# Extracted from statnett/KGraphPy@38859be62f : tests/test_header.py
# region: test_repair_blank_header_subject_dctidentifier (lines 674-688, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, URIRef, Literal, BNode, Node
from rdflib.namespace import DCAT, DCTERMS, RDF
from kgraphpy.namespaces import MD
from kgraphpy.header import CIMMetadataHeader, create_header_attribute

@pytest.mark.parametrize(
        "header_type", [MD.FullModel, DCAT.Dataset]
)
def test_repair_blank_header_subject_dctidentifier(header_type: Node, caplog: pytest.LogCaptureFixture) -> None:
    g = Graph()
    b = BNode()
    g.add((b, RDF.type, header_type))
    g.add((b, DCTERMS.identifier, Literal("1234")))

    header = CIMMetadataHeader.from_graph(g)

    assert header.subject == URIRef("urn:uuid:1234")
    records = caplog.messages
    assert len(records) == 1
    assert "blank node" in records[0]
