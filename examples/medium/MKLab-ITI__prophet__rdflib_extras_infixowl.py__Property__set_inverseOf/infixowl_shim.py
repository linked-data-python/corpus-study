"""Context shim for this example, imported identically by both sides.

`classOrIdentifier` is copied verbatim from
MKLab-ITI/prophet@eee2ab51de rdflib/extras/infixowl.py (lines 237-243).
`Class` and `Property` are reduced to the marker classes that the isinstance
test needs: the region only ever reads their `.identifier`.
"""
from rdflib import BNode, URIRef


class Class(object):
    """Stand-in for infixowl.Class (only `.identifier` matters here)."""

    def __init__(self, identifier):
        self.identifier = identifier


class Property(object):
    """Stand-in for infixowl.Property (only `.identifier` matters here)."""

    def __init__(self, identifier):
        self.identifier = identifier


def classOrIdentifier(thing):
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing
