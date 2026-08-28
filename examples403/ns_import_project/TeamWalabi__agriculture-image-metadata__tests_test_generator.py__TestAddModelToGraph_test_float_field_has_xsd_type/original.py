# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : tests/test_generator.py
# region: TestAddModelToGraph.test_float_field_has_xsd_type (lines 375-382, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from agri_image_meta.ontology.generator import (
    add_model_to_graph,
    add_property_shapes,
    generate_class,
    generate_ontology,
    generate_shacl,
    get_model_class_uri,
    get_model_shape_uri,
)

def test_float_field_has_xsd_type(self):
    cam = _make_camera(focalLength=8.0)
    g = Graph()
    uri = add_model_to_graph(g, cam)
    from agri_image_meta.utils.namespaces import EXIF
    values = list(g.objects(uri, URIRef(str(EXIF) + "FocalLength")))
    assert len(values) == 1
    assert values[0].datatype == XSD.double
