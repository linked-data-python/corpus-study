# Extracted from statnett/KGraphPy@38859be62f : tests/test_utilities.py
# region: test_extract_subjects_by_object_type_literalsubject (lines 468-472, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode, Dataset
from rdflib.namespace import RDF, RDFS, DCAT
from kgraphpy.namespaces import MD
from kgraphpy.utilities import (
    extract_uuid,
    _extract_uuid_from_urn, 
    load_cimxml_graph,
    load_graphs_from_cimxml,
    collect_cimxml_to_dataset,
    extract_subjects_by_object_type,
    load_graphs_from_trig,
)

def test_extract_subjects_by_object_type_literalsubject():
    g = Graph()
    g.add((Literal("s1"), RDF.type, MD.FullModel))
    result = extract_subjects_by_object_type(g, [MD.FullModel])
    assert result == [Literal("s1")]
