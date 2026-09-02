# Context shim (see meta.json): subset of kif_lib/rdflib.py and kif_lib/typing.py
# from IBM/kif@4ce99d0d9b, so the region executes outside the package (the
# real file does `from ..rdflib import DefinedNamespace, Namespace, URIRef`
# and `from ..typing import Final`, relative imports that need a real parent
# package to resolve).
#
# kif_lib/rdflib.py is itself a pure re-export of rdflib's own symbols (no
# wrapping, no behaviour change); kif_lib/typing.py re-exports Final from the
# standard library the same way. This shim is those same re-exports,
# narrowed to what this region uses.
#
# Identical for both representations.
from rdflib import Namespace, URIRef
from rdflib.namespace import DefinedNamespace
from typing import Final
