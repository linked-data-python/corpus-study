"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_obj_property.py__set_cardinality_relations.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair
from rdflib import Graph

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
#
# set_cardinality_relations(property_dict, ontouml_graph) returns None and
# mutates ontouml_graph in place, so the pair comparison happens through the
# call[i].arg[1] graph (see rdfeval.harness._compare_value).  Each case is a
# zero-arg callable so a fresh Graph() is built per side.
VERDICT = run_pair(
    __file__,
    entry='set_cardinality_relations',
    calls=[
        # normal range: exercises the typed lowerBound (coercion_datatype).
        lambda: (({"cardinality": "0..3", "id": "prop-range"}, Graph()), {}),
        # "*" cardinality: lower_bound="0" (typed), upper_bound="*" (plain).
        lambda: (({"cardinality": "*", "id": "prop-star"}, Graph()), {}),
        # unparsable, unrepairable, policy="preserve": bounds stay None, the
        # lowerBound/upperBound triples must NOT be emitted on either side.
        lambda: (({"cardinality": "not-a-cardinality", "id": "prop-invalid"}, Graph()), {}),
    ],
)
