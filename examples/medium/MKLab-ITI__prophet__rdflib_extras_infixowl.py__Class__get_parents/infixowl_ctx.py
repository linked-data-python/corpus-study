"""Context shim for the four infixowl regions (identical file in each example).

MKLab-ITI/prophet@eee2ab51de vendors an old copy of RDFLib's
``rdflib/extras/infixowl.py``.  Every extracted region is a single
function/method taken out of that 2000-line module, so it needs the names
defined around it: ``Class``, ``Individual``, ``Property``, ``Ontology``,
``OWLRDFListProxy`` and ``classOrIdentifier``.

Rather than copying 2000 lines of vendored code, those surrounding names are
re-exported here from the maintained upstream module the vendored file is a
copy of (``rdflib.extras.infixowl``, rdflib 7.x, API-compatible for the names
used by the regions).  ``original.py`` and ``translated.ldpy`` import this
shim identically; only the extracted region itself differs between them.
"""

from rdflib.extras.infixowl import (  # noqa: F401
    Class,
    Individual,
    OWLRDFListProxy,
    Ontology,
    Property,
    classOrIdentifier,
)
