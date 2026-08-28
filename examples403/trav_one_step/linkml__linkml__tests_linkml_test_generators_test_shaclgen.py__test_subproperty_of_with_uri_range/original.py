# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_shaclgen.py
# region: test_subproperty_of_with_uri_range (lines 1147-1202, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF, RDFS, SH, Literal, URIRef
from rdflib.collection import Collection
from linkml.generators.shaclgen import ShaclGenerator

def test_subproperty_of_with_uri_range():
    """Test that subproperty_of with uri range generates URIRef values."""
    schema_yaml = """
id: https://example.org/test
name: test

prefixes:
  ex: https://example.org/
  linkml: https://w3id.org/linkml/

imports:
  - linkml:types

default_prefix: ex

slots:
  related_to:
    slot_uri: ex:related_to
  causes:
    is_a: related_to
    slot_uri: ex:causes

  predicate:
    range: uri
    subproperty_of: related_to

classes:
  Association:
    slots:
      - predicate
"""
    gen = ShaclGenerator(schema_yaml)
    shacl = gen.serialize()
    g = rdflib.Graph()
    g.parse(data=shacl)

    # Find the property shape for predicate
    association_uri = URIRef("https://example.org/Association")
    predicate_property = None
    for prop_node in g.objects(association_uri, SH.property):
        path = list(g.objects(prop_node, SH.path))
        if path and str(path[0]) == "https://example.org/predicate":
            predicate_property = prop_node
            break

    assert predicate_property is not None

    # Get the sh:in values - should be full URIs
    sh_in_nodes = list(g.objects(predicate_property, SH["in"]))
    in_values = list(Collection(g, sh_in_nodes[0]))

    expected_uris = [
        URIRef("https://example.org/causes"),
        URIRef("https://example.org/related_to"),
    ]
    assert sorted(in_values, key=str) == expected_uris
