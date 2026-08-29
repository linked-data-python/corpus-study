# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_owlgen.py
# region: test_owlgen (lines 29-91, stratum trav_existence)
# licence of the source repository: see meta.json
import pytest
from rdflib import RDFS, SKOS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, XSD
from linkml.generators.owlgen import MetadataProfile, OwlSchemaGenerator
KS = Namespace("https://w3id.org/linkml/tests/kitchen_sink/")
BIZ = Namespace("https://example.org/bizcodes/")

@pytest.mark.parametrize(
    "metaclasses,type_objects",
    [
        (False, False),
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_owlgen(kitchen_sink_path, metaclasses, type_objects):
    """tests generation of owl schema-style ontologies"""
    owl = OwlSchemaGenerator(
        kitchen_sink_path,
        mergeimports=False,
        metaclasses=metaclasses,
        type_objects=type_objects,
        ontology_uri_suffix=".owl.ttl",
    ).serialize()
    g = Graph()
    g.parse(data=owl, format="turtle")
    owl_classes = list(g.subjects(RDF.type, OWL.Class))
    assert len(owl_classes) > 10
    for c in owl_classes:
        types = list(g.objects(c, RDF.type))
        assert OWL.Class in types
        if metaclasses:
            # TODO: make this stricter;
            # ClassDefinitions should be of type ClassDefinition
            # PVs should be of the enum type
            assert len(types) == 2
        else:
            assert len(types) == 1
    assert KS.MedicalEvent in owl_classes
    # test that enums are treated as classes
    assert KS.EmploymentEventType in owl_classes
    owl_object_properties = list(g.subjects(RDF.type, OWL.ObjectProperty))
    assert len(owl_object_properties) > 10
    for p in owl_object_properties:
        types = list(g.objects(p, RDF.type))
        assert OWL.ObjectProperty in types
        if metaclasses:
            assert len(types) == 2
        else:
            assert len(types) == 1
    owl_datatype_properties = list(g.subjects(RDF.type, OWL.DatatypeProperty))
    if type_objects:
        assert owl_datatype_properties == []
    else:
        assert len(owl_datatype_properties) > 10
    for p in owl_datatype_properties:
        types = list(g.objects(p, RDF.type))
        assert OWL.DatatypeProperty in types
        if metaclasses:
            assert len(types) == 2
        else:
            assert len(types) == 1
    # check that definitions are present, and use the default profile
    assert Literal("A person, living or dead") in g.objects(KS.Person, SKOS.definition)
    # test enums
    enum_bnode = list(g.objects(KS.EmploymentEventType, OWL.unionOf))[0]
    coll = Collection(g, enum_bnode)
    assert [BIZ["001"], BIZ["002"], BIZ["003"], BIZ["004"]] == list(coll)
    assert BIZ["001"] in owl_classes
