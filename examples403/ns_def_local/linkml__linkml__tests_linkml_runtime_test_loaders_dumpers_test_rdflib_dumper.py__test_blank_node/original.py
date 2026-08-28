# Extracted from linkml/linkml@680595df54 : tests/linkml_runtime/test_loaders_dumpers/test_rdflib_dumper.py
# region: test_blank_node (lines 239-262, stratum ns_def_local)
# licence of the source repository: see meta.json
import pytest
from curies import Converter
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS, XSD
from linkml_runtime.dumpers import rdflib_dumper, yaml_dumper
from linkml_runtime.loaders import rdflib_loader, yaml_loader
from linkml_runtime.utils.schemaview import SchemaView
from tests.linkml_runtime.test_loaders_dumpers.models.personinfo import (
    Address,
    Container,
    Organization,
    OrganizationType,
    Person,
)
SCHEMA = INPUT_PATH / "personinfo.yaml"
BLANK_NODE_TTL = INPUT_PATH / "blank_node_test.ttl"
PREFIX_MAP = {
    "CODE": "http://example.org/code/",
    "ROR": "http://example.org/ror/",
    "P": "http://example.org/P/",
    "GEO": "http://example.org/GEO/",
}

@pytest.mark.parametrize("prefix_map", [PREFIX_MAP, Converter.from_prefix_map(PREFIX_MAP)])
def test_blank_node(prefix_map):
    """
    blank nodes should be retrievable
    """
    view = SchemaView(str(SCHEMA))
    address: Address = rdflib_loader.load(
        str(BLANK_NODE_TTL),
        target_class=Address,
        schemaview=view,
        prefix_map=prefix_map,
        ignore_unmapped_predicates=True,
    )
    assert address.city == "foo city"
    ttl = rdflib_dumper.dumps(address, schemaview=view)
    print(ttl)
    g = Graph()
    g.parse(data=ttl, format="ttl")
    INFO = Namespace("https://w3id.org/linkml/examples/personinfo/")
    SDO = Namespace("http://schema.org/")
    [bn] = g.subjects(RDF.type, SDO.PostalAddress)
    assert (bn, RDF.type, SDO.PostalAddress) in g
    assert (bn, INFO.city, Literal("foo city")) in g
    assert (bn, INFO.street, Literal("1 foo street")) in g
