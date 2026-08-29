# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/tests/test_extractor_connectives.py
# region: test_connective_operation_mapping (lines 142-148, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib
import lib.shacl_properties_to_sql as props

def test_connective_operation_mapping():
    sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
    assert props.connective_operation(sh['or']) == 'OR'
    assert props.connective_operation(sh['and']) == 'AND'
    assert props.connective_operation(sh.xone) == 'XONE'
    assert props.connective_operation(sh['not']) == 'NOT'
    assert props.connective_operation(None) == 'OR'
