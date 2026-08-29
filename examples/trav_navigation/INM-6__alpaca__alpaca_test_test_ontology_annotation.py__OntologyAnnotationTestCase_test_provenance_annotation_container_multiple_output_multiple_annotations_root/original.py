# Extracted from INM-6/alpaca@2b8dd34fc6 : alpaca/test/test_ontology_annotation.py
# region: OntologyAnnotationTestCase.test_provenance_annotation_container_multiple_output_multiple_annotations_root (lines 767-828, stratum trav_navigation)
# licence of the source repository: see meta.json
import io
from rdflib import Literal, URIRef, Namespace, Graph, RDF, PROV
from alpaca import activate, deactivate, Provenance, save_provenance
from alpaca.ontology import ALPACA

def test_provenance_annotation_container_multiple_output_multiple_annotations_root(self):
    activate(clear=True)
    container = process_multiple_container_output_multiple_annotations_root()
    deactivate()

    prov_data = save_provenance()

    # Read PROV information as RDF
    prov_graph = Graph()
    with io.StringIO(prov_data) as data_stream:
        prov_graph.parse(data_stream, format='turtle')

    # Check that the annotations exist
    self.assertEqual(
        len(list(prov_graph.triples(
            (None, RDF.type, self.ONTOLOGY.ProcessMultipleContainerOutputMultipleAnnotationsRoot)))
        ), 1)
    self.assertEqual(
        len(list(prov_graph.triples(
            (None, RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel2)))
        ), 6)
    self.assertEqual(
        len(list(prov_graph.triples(
            (None, RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel1)))
        ), 2)
    self.assertEqual(
        len(list(prov_graph.triples(
            (None, RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel0)))
        ), 1)

    # FunctionExecution is ProcessMultipleContainerOutputMultipleAnnotationsRoot
    execution_uri = list(
        prov_graph.subjects(RDF.type, ALPACA.FunctionExecution))[0]
    self.assertTrue((execution_uri, RDF.type,
                     self.ONTOLOGY.ProcessMultipleContainerOutputMultipleAnnotationsRoot) in prov_graph)

    # Check returned values
    output_nodes = prov_graph.subjects(RDF.type,
                            self.ONTOLOGY.ProcessedMultipleContainerOutputLevel0)
    for output_level0 in output_nodes:
        self.assertTrue((output_level0, PROV.wasGeneratedBy, execution_uri) in prov_graph)
        self.assertTrue((output_level0,
                         RDF.type, ALPACA.DataObjectEntity) in prov_graph)
        self.assertTrue((output_level0,
                         RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel0)
                        in prov_graph)
        members = list(prov_graph.objects(output_level0, PROV.hadMember))
        self.assertEqual(len(members), 2)
        for output_level1 in prov_graph.objects(output_level0, PROV.hadMember):
            self.assertTrue(
                (output_level1, RDF.type, ALPACA.DataObjectEntity) in prov_graph)
            self.assertTrue(
                (output_level1, RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel1) in prov_graph)
            members = list(prov_graph.objects(output_level1, PROV.hadMember))
            self.assertEqual(len(members), 3)
            for output_level2 in prov_graph.objects(output_level1, PROV.hadMember):
                self.assertTrue(
                    (output_level2, RDF.type, ALPACA.DataObjectEntity) in prov_graph)
                self.assertTrue(
                    (output_level2, RDF.type, self.ONTOLOGY.ProcessedMultipleContainerOutputLevel2) in prov_graph)
                members = list(prov_graph.objects(output_level2, PROV.hadMember))
                self.assertEqual(len(members), 0)
