"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_main.py__decode_dictionary.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph
from rdfeval.harness import run_pair


def _fixture():
    dictionary_data = {
        "id": "class-1",
        "type": "Class",
        "name": "Person",
        "description": "A person class.",
        "width": 120,
        "height": -5,  # invalid: negative -> LOGGER.error + skipped, no triple
        "isAbstract": True,  # plain literal branch
        "x": 42,  # restricted field: never reaches the object branches
        "attributes": [
            {"id": "attr-1", "type": "Property", "name": "attrName"},
            "not-a-dict-so-skipped",
        ],
        "container": {"id": "nested-1", "type": "Something", "width": 7},
    }
    return (dictionary_data, Graph(), "en"), {}


VERDICT = run_pair(
    __file__,
    entry='decode_dictionary',
    calls=[_fixture, _fixture],
)
