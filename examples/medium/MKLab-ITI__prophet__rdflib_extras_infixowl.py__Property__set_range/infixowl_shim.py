# Context shim (see meta.json).  The extracted region is one method/function of
# MKLab-ITI/prophet@eee2ab51de, rdflib/extras/infixowl.py -- which is a vendored
# copy of RDFLib's own rdflib.extras.infixowl.  That vendored copy targets
# rdflib 3.x (it imports rdflib.py3compat, gone since rdflib 4), so it cannot be
# imported here; the surrounding module context the region needs is therefore
# taken from the maintained descendant of that very module, rdflib 7.2.1's
# rdflib.extras.infixowl, whose definitions of the names below are unchanged
# apart from PEP8 renamings that do not touch these signatures.
#
# This module is imported IDENTICALLY by original.py and translated.ldpy.
from rdflib.extras.infixowl import (  # noqa: F401
    BooleanClass,
    CastClass,
    Class,
    Individual,
    Property,
    classOrIdentifier,
    manchesterSyntax,
    some,
)
