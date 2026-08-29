# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_utils.py
# region: test_convert_jsonschema_to_shacl (lines 32-35, stratum trav_one_step)
# licence of the source repository: see meta.json
from nanopub.fdo.utils import (
    fix_numeric_shacl_constraints,
    looks_like_handle,
    handle_to_iri,
    convert_jsonschema_to_shacl
)

def test_convert_jsonschema_to_shacl():
    schema = {"required": ["field1", "field2"]}
    g = convert_jsonschema_to_shacl(schema)
    assert len(list(g.subjects())) > 0
