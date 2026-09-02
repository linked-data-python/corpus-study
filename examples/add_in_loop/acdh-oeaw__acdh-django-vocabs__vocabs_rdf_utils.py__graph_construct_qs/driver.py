"""Validation driver for acdh-oeaw__acdh-django-vocabs__vocabs_rdf_utils.py__graph_construct_qs.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair


class _Notes:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def __eq__(self, other):
        return isinstance(other, _Notes) and self._items == other._items


class _Obj:
    def __init__(self, notes):
        self.has_notes = _Notes(notes)

    def __eq__(self, other):
        return isinstance(other, _Obj) and self.has_notes == other.has_notes


class _Note:
    def __init__(self, note_type, name, language):
        self.note_type = note_type
        self.name = name
        self.language = language

    def __eq__(self, other):
        return (
            isinstance(other, _Note)
            and self.note_type == other.note_type
            and self.name == other.name
            and self.language == other.language
        )


def _call_all_branches():
    # One note per branch of the original if/elif chain, plus an unknown
    # note_type that must fall into the `else` (skos:note) branch.
    notes = [
        _Note('note', 'a general note', 'en'),
        _Note('scopeNote', 'the scope', 'en'),
        _Note('changeNote', 'what changed', 'en'),
        _Note('editorialNote', 'editorial remark', 'de'),
        _Note('historyNote', 'history', 'en'),
        _Note('definition', 'a definition', 'en'),
        _Note('example', 'an example', 'fr'),
        _Note('somethingElse', 'unmapped falls back to skos:note', 'en'),
    ]
    obj = _Obj(notes)
    concept = URIRef("https://vocabs.acdh.oeaw.ac.at/example/concept/1")
    return (obj, concept, Graph()), {}


def _call_no_notes():
    obj = _Obj([])
    concept = URIRef("https://vocabs.acdh.oeaw.ac.at/example/concept/2")
    return (obj, concept, Graph()), {}


VERDICT = run_pair(
    __file__,
    entry='graph_construct_qs_notes',
    calls=[_call_all_branches, _call_no_notes],
)
