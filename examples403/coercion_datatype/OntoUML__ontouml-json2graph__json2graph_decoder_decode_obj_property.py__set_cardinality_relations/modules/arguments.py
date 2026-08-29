# Context shim (see meta.json): the two ARGUMENTS keys this region reads
# (base_uri, invalid_cardinality_policy), set to the same defaults
# OntoUML/ontouml-json2graph@982f12b9c4 json2graph/modules/arguments.py's
# argument-initialisation function uses for library/test-mode execution
# (base_uri="https://example.org#", invalid_cardinality_policy="preserve").
# Identical for both representations.
ARGUMENTS = {
    "base_uri": "https://example.org#",
    "invalid_cardinality_policy": "preserve",
}
