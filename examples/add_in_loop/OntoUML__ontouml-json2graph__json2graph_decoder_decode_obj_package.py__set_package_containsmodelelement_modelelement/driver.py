"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_obj_package.py__set_package_containsmodelelement_modelelement.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph

from rdfeval.harness import run_pair


def _call_multi():
    # A package containing several elements: exercises the loop over more
    # than one row.
    package_dict = {
        "id": "package-1",
        "contents": [{"id": "class-1"}, {"id": "class-2"}, {"id": "relation-1"}],
    }
    return (package_dict, Graph()), {}


def _call_single():
    # A package containing exactly one element: the loop runs once.
    package_dict = {
        "id": "package-2",
        "contents": [{"id": "class-3"}],
    }
    return (package_dict, Graph()), {}


def _call_empty_contents():
    # "contents" present but empty: the guarding `if package_id_contents_list`
    # must add nothing.
    package_dict = {"id": "package-3", "contents": []}
    return (package_dict, Graph()), {}


def _call_no_contents():
    # No "contents" key at all: get_package_contents returns [], same guard.
    package_dict = {"id": "package-4"}
    return (package_dict, Graph()), {}


VERDICT = run_pair(
    __file__,
    entry='set_package_containsmodelelement_modelelement',
    calls=[_call_multi, _call_single, _call_empty_contents, _call_no_contents],
)
