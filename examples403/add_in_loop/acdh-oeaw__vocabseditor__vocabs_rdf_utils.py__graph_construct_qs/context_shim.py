# Context shim (see meta.json), for
# acdh-oeaw/vocabseditor@bf418c87b3 : vocabs/rdf_utils.py.
#
# graph_construct_qs receives `results`, a Django QuerySet of Concept model
# instances, and reads `.scheme`/`.collection`/`.has_members` (Django
# ForeignKey/related managers) and `.get_subject()`/`.as_graph()`/
# `.create_uri()` (methods defined on the app's Concept/Collection/
# ConceptScheme models, in vocabs/models.py -- not in the extracted region,
# and requiring the full Django ORM to instantiate for real). Reproducing
# the actual Django models is out of scope for a standalone region; these
# are minimal duck-typed stand-ins exposing exactly the methods/attributes
# graph_construct_qs reads, nothing else.
#
# Identical bindings for both representations.
from rdflib import Graph


class QuerySetStub(list):
    """Stands in for a Django QuerySet / related manager: `.first()` and
    `.all()` are the only two QuerySet methods this region calls."""

    def first(self):
        return self[0] if self else None

    def all(self):
        return self


class ModelStub:
    """Stands in for a Concept/Collection/ConceptScheme model instance:
    `.get_subject()`, `.as_graph()`, `.create_uri()` are real methods of
    those models (vocabs/models.py, not part of the extracted region);
    any other field (`.scheme`, `.collection`, `.creator`, `.contributor`,
    `.has_members`, `.legacy_id`) is set directly as a keyword argument."""

    def __init__(self, subject=None, graph=None, uri=None, **fields):
        self._subject = subject
        self._graph = graph if graph is not None else Graph()
        self._uri = uri
        for key, value in fields.items():
            setattr(self, key, value)

    def get_subject(self):
        return self._subject

    def as_graph(self):
        return self._graph

    def create_uri(self):
        return self._uri
