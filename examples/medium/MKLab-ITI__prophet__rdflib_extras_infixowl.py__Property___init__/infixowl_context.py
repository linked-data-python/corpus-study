"""Context shim for the MKLab-ITI/prophet regions.

The reviewed regions come from ``rdflib/extras/infixowl.py`` of
MKLab-ITI/prophet@eee2ab51de, which is a *vendored copy* of rdflib's
``rdflib.extras.infixowl``.  Each region is a single method lifted out of
its class, so it needs the surrounding module context (the class
hierarchy and the ``classOrIdentifier`` / ``propertyOrIdentifier``
helpers).

The vendored copy cannot be imported as-is under rdflib 7 (its first line
is ``from rdflib import py3compat``, removed years ago).  We therefore
re-export the maintained upstream implementation shipped with the
installed rdflib, whose names and signatures are identical to the
vendored ones for everything the regions touch (verified against
corpus/repos/MKLab-ITI__prophet/rdflib/extras/infixowl.py:
``Individual.__init__``, ``AnnotatableTerms.__init__``, ``Class``,
``Property.__init__``, ``Restriction.__init__``, ``classOrIdentifier``,
``propertyOrIdentifier``, ``first``).

This module is imported IDENTICALLY by original.py and translated.ldpy.
"""

from rdflib import BNode, Literal, Namespace, RDF, RDFS, URIRef, Variable  # noqa: F401
from rdflib.graph import Graph  # noqa: F401
from rdflib.term import Identifier  # noqa: F401
from rdflib.util import first  # noqa: F401
from rdflib.extras.infixowl import (  # noqa: F401
    AnnotatableTerms,
    Class,
    Individual,
    Property,
    Restriction,
    classOrIdentifier,
    propertyOrIdentifier,
)

# The vendored copy declares its own OWL namespace object under this name.
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
