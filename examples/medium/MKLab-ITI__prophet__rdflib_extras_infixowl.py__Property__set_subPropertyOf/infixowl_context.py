# Context shim (see meta.json): the region calls ``classOrIdentifier``, a
# module-level helper of the vendored ``rdflib/extras/infixowl.py`` in
# MKLab-ITI/prophet@eee2ab51de.  That vendored module cannot be imported
# against the rdflib installed here (its first line is
# ``from rdflib import py3compat``, removed in rdflib 6), so the helper is
# copied verbatim; ``Class`` and ``Property`` — only needed by its isinstance
# test — come from ``rdflib.extras.infixowl``, the upstream of that vendored
# copy (the two definitions differ only in formatting).
# Used identically by original.py and translated.ldpy.
from rdflib import BNode, URIRef
from rdflib.extras.infixowl import Class, Property


def classOrIdentifier(thing):
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing
