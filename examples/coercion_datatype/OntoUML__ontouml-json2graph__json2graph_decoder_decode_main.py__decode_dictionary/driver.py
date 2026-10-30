"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_main.py__decode_dictionary.

Establishes semantic equivalence of original.py and translated.ldpy.

decode_dictionary returns None and writes into its `ontouml_graph` argument,
compared by isomorphism after each call (rdfeval.harness compares every call
argument); what it logs and warns is compared as the call's stdout.

Repair of 2026-10-30 (triage: weak-oracle).  The first two calls (the
original fixture) only pass language='en', a valid width and a negative
height.  The calls added below exercise each way a value reaching the
rewritten islands can differ:

  * the shim's logger and Text.value hook did nothing observable (the
    logger writes to stderr, which the harness does not capture; the hook
    was a no-op).  Both are made recorders HERE, identically for both
    sides: a handler printing each LOGGER record to the current stdout,
    and a hook printing each call (the real one, text_values.py, warns
    only on a value not in (None, "")).  Both modules import the patched
    hook, since they are executed after this patch;
  * language='' -- the repository's default (decode.py:68,
    library.py:13): `name` takes the plain-literal branch;
  * the width/height guard on every type a JSON number or value can have
    (json.loads; clean_null_data removes nulls first, decode_main.py:137):
    0 (the bound, valid), a large int, True and False (`type(...) is not
    int` rejects bool), a float, an integral float, a string;
  * falsy plain values (`""`, False, 0, an empty name with a language);
  * a Text with a non-empty and an empty `value` (hook called, no triple)
    beside a non-Text `value` (a plain triple);
  * the graph the repository passes (decode_main.py:131-133: bindings
    `ontouml` and the base), already holding a triple, for a dictionary
    without `id` (nothing added) and for a nested element without `type`
    (KeyError on both sides after the outer triples were written: the
    partial graph is compared too).
"""
import logging
import sys

from rdflib import Graph, Literal, URIRef

import ontouml_shim
from rdfeval.harness import run_pair


class _ToStdout(logging.Handler):
    def emit(self, record):
        print(f"{record.levelname}: {record.getMessage()}", file=sys.stdout)


_logger = logging.getLogger("ontouml_json2graph_shim")
_logger.addHandler(_ToStdout())
_logger.propagate = False


def _text_hook(text_shape):
    print(f"text-value hook: {text_shape['id']} {text_shape.get('value')!r}")


ontouml_shim.warn_if_text_value_is_unsupported = _text_hook


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


def _repo_graph():
    """The graph decode_json_to_graph builds, plus one earlier triple."""
    g = Graph()
    g.bind("ontouml", "https://w3id.org/ontouml#")
    g.bind("", "https://example.org/ontouml/")
    g.add((URIRef("https://example.org/ontouml/earlier"),
           URIRef("https://w3id.org/ontouml#name"), Literal("kept")))
    return g


def call(data, language):
    return lambda: ((data, _repo_graph(), language), {})


DIMENSIONS = {
    "id": "diagram-1", "type": "Diagram",
    "contents": [
        {"id": "s0", "type": "ClassView", "width": 0, "height": 10**20},
        {"id": "s1", "type": "ClassView", "width": True, "height": False},
        {"id": "s2", "type": "ClassView", "width": 12.5, "height": 30.0},
        {"id": "s3", "type": "ClassView", "width": "40", "height": -1},
    ],
}
FALSY_AND_TEXT = {
    "id": "pkg-1", "type": "Package", "name": "",
    "description": "", "isAbstract": False, "isOrdered": 0,
    "contents": [
        {"id": "t1", "type": "Text", "value": "a note"},
        {"id": "t2", "type": "Text", "value": ""},
        {"id": "c1", "type": "Class", "value": "not a Text", "name": "Car"},
    ],
}
NO_ID = {"type": "Path", "name": "never decoded", "width": 3}
NO_TYPE_INSIDE = {
    "id": "pkg-2", "type": "Package", "name": "Outer", "width": 5,
    "contents": [{"id": "orphan", "name": "no type"}],
}


VERDICT = run_pair(
    __file__,
    entry='decode_dictionary',
    calls=[
        _fixture, _fixture,
        lambda: ((_fixture()[0][0], Graph(), ""), {}),  # repo default lang
        call(DIMENSIONS, ""),
        call(FALSY_AND_TEXT, "en"),
        call(FALSY_AND_TEXT, ""),
        call(NO_ID, "en"),
        call(NO_TYPE_INSIDE, "en"),
    ],
)
