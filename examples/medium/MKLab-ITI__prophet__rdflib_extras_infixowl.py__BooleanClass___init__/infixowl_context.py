# Context shim (see meta.json): the region is BooleanClass.__init__ of the
# vendored ``rdflib/extras/infixowl.py`` in MKLab-ITI/prophet@eee2ab51de and
# calls ``Class.__init__`` and ``OWLRDFListProxy.__init__`` of that same file.
# The vendored module cannot be imported against the rdflib installed here
# (its first line is ``from rdflib import py3compat``, removed in rdflib 6),
# so those two classes are taken from ``rdflib.extras.infixowl`` — the
# upstream of the vendored copy, whose ``Class.__init__`` and
# ``OWLRDFListProxy.__init__`` differ from the vendored ones only in
# formatting (verified against the checkout).
# Used identically by original.py and translated.ldpy.
from rdflib.extras.infixowl import (  # noqa: F401
    BooleanClass,
    Class,
    OWLRDFListProxy,
    classOrIdentifier,
)
