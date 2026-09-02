"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_obj_class.py__set_class_restrictedto_ontologicalnature.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph

from rdfeval.harness import run_pair


def _call_multi():
    # A class restricted to several natures: exercises the loop over more
    # than one row.
    class_dict = {
        "id": "class-1",
        "restrictedTo": ["abstract", "collective", "type"],
    }
    return (class_dict, Graph()), {}


def _call_single():
    # A class restricted to exactly one nature: the loop runs once.
    class_dict = {
        "id": "class-2",
        "restrictedTo": ["relator"],
    }
    return (class_dict, Graph()), {}


def _call_absent():
    # No "restrictedTo" key at all: the guarding `if` must add nothing.
    class_dict = {"id": "class-3"}
    return (class_dict, Graph()), {}


VERDICT = run_pair(
    __file__,
    entry='set_class_restrictedto_ontologicalnature',
    calls=[_call_multi, _call_single, _call_absent],
)
