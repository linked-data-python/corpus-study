# Context shim (see meta.json): subset of kif_lib/rdflib.py from IBM/kif@4ce99d0d9b,
# so the region executes outside the package (the real file does
# `from ..rdflib import DefinedNamespace, Namespace, URIRef`, a relative
# import that needs a real parent package to resolve).
#
# kif_lib/rdflib.py is itself a pure re-export of rdflib's own symbols (no
# wrapping, no behaviour change), so this shim is the same re-export,
# narrowed to what this region uses.
#
# Identical for both representations.
from rdflib import Namespace, URIRef
from rdflib.namespace import DefinedNamespace
