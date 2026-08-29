# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_owlgen.py
# region: test_slot_cardinality_axioms (lines 1087-1100, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDFS, SKOS, BNode, Graph, Literal, Namespace, URIRef

if expected_exact is not None:
    assert Literal(expected_exact) in exact_values
    assert not min_values, f"expected no owl:minCardinality when min==max, got {min_values}"
    assert not max_values, f"expected no owl:maxCardinality when min==max, got {max_values}"
else:
    assert not exact_values, f"expected no owl:cardinality, got {exact_values}"
    if expected_min is not None:
        assert Literal(expected_min) in min_values
    else:
        assert not min_values, f"expected no owl:minCardinality, got {min_values}"
    if expected_max is not None:
        assert Literal(expected_max) in max_values
    else:
        assert not max_values, f"expected no owl:maxCardinality, got {max_values}"
