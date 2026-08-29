# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_shaclgen.py
# region: test_exclude_imports (lines 766-787, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF, RDFS, SH, Literal, URIRef
from linkml.generators.shaclgen import ShaclGenerator

def test_exclude_imports(input_path):
    shacl = ShaclGenerator(
        input_path("shaclgen/exclude_imports.yaml"), mergeimports=True, exclude_imports=True
    ).serialize()
    print(shacl)

    g = rdflib.Graph()
    g.parse(data=shacl)

    # Check there is a single class from the source LinkML file, not the extended classes
    classes = list(g.subjects(RDF.type, SH.NodeShape))

    assert classes == [URIRef("https://example.org/ExtendedClass")]

    # Check that the single extending class has its slots and inherited slots too from the extended class
    property_paths = []
    for subject_node, property_node in g.subject_objects(URIRef("http://www.w3.org/ns/shacl#property")):
        property_paths.append(str(next(g.objects(property_node, SH.path, True))))

    assert len(property_paths) == 2
    assert "https://example.org/extendedProperty" in property_paths
    assert "https://example.org/baseProperty" in property_paths
