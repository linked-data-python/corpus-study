# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : tests/test_ontology.py
# region: TestCompleteWorkflow.test_complete_workflow (lines 166-207, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph
from agri_image_meta.schemas.images import ImageMetadata
from agri_image_meta.schemas.field import FieldMetadata, PlotMetadata
from agri_image_meta.schemas.camera import CameraMetadata
from agri_image_meta.schemas.crop import CropMetadata
from agri_image_meta.schemas.platform import PlatformMetadata
from agri_image_meta.schemas.dataset import DatasetMetadata
from agri_image_meta.ontology.generator import (
    generate_ontology,
    generate_shacl,
    add_model_to_graph,
)
from agri_image_meta.data.example_data import (
    dummy_dataset,
)

def test_complete_workflow(self):
    """Test the complete workflow: generate ontology, populate graph, and query."""
    # Step 1: Generate ontology
    models = [
        ImageMetadata,
        CameraMetadata,
        PlatformMetadata,
        FieldMetadata,
        PlotMetadata,
        CropMetadata,
        DatasetMetadata,
    ]
    ontology_graph = generate_ontology(models)
    assert len(ontology_graph) > 0

    # Step 2: Generate SHACL shapes
    shapes_graph = generate_shacl(models)
    assert len(shapes_graph) > 0

    # Step 3: Create sample data
    dataset = dummy_dataset

    # Step 4: Populate RDF graph
    data_graph = Graph()
    add_model_to_graph(data_graph, dataset)
    assert len(data_graph) > 0

    # # Step 5: Query the data
    # results = query_images_by_location_and_properties(data_graph, field_ids=["field_001"])
    # assert len(results) >= 1

    # Step 6: Verify data exists
    query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    SELECT ?image ?imageName WHERE {
        ?image a agimage:Image ;
            <https://w3id.org/agri-image/imageName> ?imageName .
    }
    """
    query_results = list(data_graph.query(query))
    assert len(query_results) == 1
    assert "20251014T093010Z857_camid9_trigger1000_rgb.png" in str(query_results[0][1])
