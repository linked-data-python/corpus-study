# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_owlgen.py
# region: test_rdfs_profile (lines 135-151, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import RDFS, SKOS, BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, XSD
from linkml.generators.owlgen import MetadataProfile, OwlSchemaGenerator
KS = Namespace("https://w3id.org/linkml/tests/kitchen_sink/")

def test_rdfs_profile(kitchen_sink_path):
    owl = OwlSchemaGenerator(
        kitchen_sink_path,
        mergeimports=False,
        metaclasses=False,
        type_objects=False,
        metadata_profile=MetadataProfile.rdfs,
        ontology_uri_suffix=".owl.ttl",
    ).serialize(mergeimports=False)
    g = Graph()
    g.parse(data=owl, format="turtle")
    owl_classes = list(g.subjects(RDF.type, OWL.Class))
    for c in owl_classes:
        # check not using the default metadata profile
        assert list(g.objects(c, SKOS.definition)) == []
    # check that definitions are present, and use the RDFS profile
    assert Literal("A person, living or dead") in g.objects(KS.Person, RDFS.comment)
