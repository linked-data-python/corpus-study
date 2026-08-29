# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_shaclgen.py
# region: test_nodeidentifier_range_produces_blank_node_or_iri (lines 1298-1357, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF, RDFS, SH, Literal, URIRef
from linkml.generators.shaclgen import ShaclGenerator

def test_nodeidentifier_range_produces_blank_node_or_iri():
    """Test that range: nodeidentifier produces sh:nodeKind sh:BlankNodeOrIRI, not sh:Literal.

    The ``nodeidentifier`` built-in type (type_uri ``shex:nonLiteral``) represents
    an IRI or blank-node reference. The SHACL generator must emit
    ``sh:nodeKind sh:BlankNodeOrIRI`` (not ``sh:Literal`` with ``sh:datatype``).
    """
    schema_yaml = """
id: https://example.org/test-nodeident
name: test_nodeident

prefixes:
  ex: https://example.org/
  linkml: https://w3id.org/linkml/

imports:
  - linkml:types

default_prefix: ex
default_range: string

slots:
  node_ref:
    range: nodeidentifier
    slot_uri: ex:nodeRef
  uri_ref:
    range: uri
    slot_uri: ex:uriRef

classes:
  Container:
    slots:
      - node_ref
      - uri_ref
"""
    gen = ShaclGenerator(schema_yaml)
    shacl = gen.serialize()
    g = rdflib.Graph()
    g.parse(data=shacl)

    container_uri = URIRef("https://example.org/Container")

    # Collect property shapes keyed by sh:path
    props = {}
    for prop_node in g.objects(container_uri, SH.property):
        path = list(g.objects(prop_node, SH.path))
        if path:
            props[str(path[0])] = prop_node

    # nodeidentifier → sh:nodeKind sh:BlankNodeOrIRI, no sh:datatype
    node_ref = props["https://example.org/nodeRef"]
    node_kinds = list(g.objects(node_ref, SH.nodeKind))
    assert SH.BlankNodeOrIRI in node_kinds, f"Expected sh:BlankNodeOrIRI for nodeidentifier, got {node_kinds}"
    assert SH.Literal not in node_kinds
    assert list(g.objects(node_ref, SH.datatype)) == []

    # uri → sh:nodeKind sh:IRI (unchanged existing behaviour)
    uri_ref = props["https://example.org/uriRef"]
    uri_kinds = list(g.objects(uri_ref, SH.nodeKind))
    assert SH.IRI in uri_kinds, f"Expected sh:IRI for uri, got {uri_kinds}"
