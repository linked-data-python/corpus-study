"""Validation driver for vlizBE__vocabserver-app__services_content-unification_sparql_util.py__sparql_construct_res_to_graph.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdfeval.harness import run_pair

EX = "http://example.org/"


def _make_res():
    return {
        "results": {
            "bindings": [
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "p"},
                    "o": {"type": "uri", "value": EX + "b"},
                },
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "label"},
                    "o": {"type": "literal", "value": "hello", "xml:lang": "en"},
                },
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "count"},
                    "o": {"type": "literal", "value": "3",
                          "datatype": "http://www.w3.org/2001/XMLSchema#integer"},
                },
                {
                    "s": {"type": "uri", "value": EX + "c"},
                    "p": {"type": "uri", "value": EX + "plain"},
                    "o": {"type": "literal", "value": "plain text"},
                },
            ]
        }
    }


VERDICT = run_pair(
    __file__,
    entry='sparql_construct_res_to_graph',
    calls=[lambda: ((_make_res(),), {})],
)
