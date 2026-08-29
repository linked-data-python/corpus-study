# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : tests/test_generator.py
# region: TestGenerateOntologyMetadata.test_ontology_type_triple (lines 112-114, stratum ns_import_project)
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
from agri_image_meta.schemas.camera import CameraMetadata
from agri_image_meta.utils.namespaces import AGIMAGE, DCT, FOAF, SOSA

def test_ontology_type_triple(self):
    g = generate_ontology([CameraMetadata])
    assert (AGIMAGE[""], RDF.type, OWL.Ontology) in g
