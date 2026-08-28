# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/tests/test_extractor_connectives.py
# region: test_disagreeing_branches_produce_no_attribute_type (lines 171-198, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
import lib.shacl_properties_to_sql as props
SPANNING = """
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix ngsild: <https://uri.etsi.org/ngsi-ld/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix iff:  <https://industry-fusion.com/types/v0.9/> .
@prefix :     <https://industry-fusion.com/shapes/v0.9/> .

:S a sh:NodeShape ; sh:targetClass iff:machine ;
    sh:property [ sh:path iff:spanning ; sh:minCount 0 ; sh:maxCount 1 ;
        sh:or ( [ sh:property [ sh:path ngsild:hasValue ;
                                sh:datatype xsd:double ] ]
                [ sh:property [ sh:path ngsild:hasValueList ;
                                sh:datatype xsd:double ] ] ) ] .
"""

def test_disagreeing_branches_produce_no_attribute_type(tmp_path):
    """
    Picking one branch's type would count only that kind of attribute and
    alert on the other -- an array value reported as a missing scalar. The
    count must span both, expressed as carrying no attribute type at all.

    This returned ('hasValue', 'Property') by sorting order before, which is
    an arbitrary choice between two equally valid branches.
    """
    sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
    g = rdflib.Graph()
    g.parse(data=SPANNING, format='turtle')
    spanning = rdflib.URIRef(
        'https://industry-fusion.com/types/v0.9/spanning')
    prop = next(s for s in g.subjects(sh.path, spanning)
                if (s, sh['or'], None) in g)

    # The guard must be what makes this (None, None): the branches have to
    # actually disagree, otherwise the assertion below passes on an empty set.
    branches = {props.VALUE_PATH_ATTRIBUTE_TYPES[str(path)]
                for clause in props.connective_clauses(g, prop)
                for value_shape in g.objects(clause, sh.property)
                for path in g.objects(value_shape, sh.path)
                if str(path) in props.VALUE_PATH_ATTRIBUTE_TYPES}
    assert len(branches) == 2, \
        f'the fixture no longer exercises disagreeing branches: {branches}'

    assert props.branch_attribute_type(g, prop) == (None, None)
