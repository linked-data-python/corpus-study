# Extracted from lazlop/semantic_objects@243c5efd8c : tests/test_inference.py
# region: test_annotation_rule_structure (lines 56-80, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from semantic_objects.inference import (
    generate_annotation_rules,
    infer_types,
    AnnotationRuleGenerator,
    InferenceEngine
)
from semantic_objects.namespaces import RDF, S223, HPFS, bind_prefixes

def test_annotation_rule_structure():
    """Test that annotation rules have the correct structure"""
    print("\n=== Testing Annotation Rule Structure ===")

    from examples.s223_framework_demo import Space

    generator = AnnotationRuleGenerator()
    rules = generator.generate_annotation_rules(Space)

    # Check for Space annotation shape
    space_annotation = HPFS["SpaceAnnotation"]
    assert (space_annotation, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")) in rules

    # Check for annotation rule
    space_rule = HPFS["SpaceAnnotationRule"]
    assert (space_annotation, URIRef("http://www.w3.org/ns/shacl#rule"), space_rule) in rules
    assert (space_rule, RDF.type, URIRef("http://www.w3.org/ns/shacl#TripleRule")) in rules

    # Check rule structure (subject, predicate, object)
    assert (space_rule, URIRef("http://www.w3.org/ns/shacl#subject"), URIRef("http://www.w3.org/ns/shacl#this")) in rules
    assert (space_rule, URIRef("http://www.w3.org/ns/shacl#predicate"), RDF.type) in rules

    print("Annotation rule structure is correct")

    return rules
