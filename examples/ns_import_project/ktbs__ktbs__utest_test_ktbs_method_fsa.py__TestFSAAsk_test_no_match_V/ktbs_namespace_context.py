# Context shim (see meta.json): the two bindings this region needs from
# ktbs/ktbs@4f9f50c770cde629c5a75a2d3f502503738bdaf0 : lib/ktbs/namespace.py
# -- KTBS_NS_URI (a plain string) and KTBS (a namespace object read via
# KTBS.fsa). The real namespace.py additionally does
# `from rdfrest.cores.local import LocalCore, Service` and
# `from rdfrest.util.helper_service import make_helper_service` to build a
# REST description service around the vocabulary graph; `rdfrest` is not on
# PyPI at all (verified: `pip index versions rdfrest` -> "No matching
# distribution found") and none of that machinery is reached by this
# region -- only the two names below are. KTBS_NS_URI and the local name
# `fsa` are copied verbatim from the real file (namespace.py lines 39-40 for
# KTBS_NS_URI; `fsa` is a real fragment of the kTBS vocabulary,
# namespace.py's own embedded Turtle: ":fsa a :BuiltinMethod ;
# rdfs:label \"Finite-state automaton\"@en"). The real KTBS is a
# rdflib.namespace.ClosedNamespace restricted to the vocabulary's own term
# set; a plain Namespace is used here since this region touches only one
# term and ClosedNamespace's closed-membership check is not part of what
# the region depends on -- same simplification as the sibling
# ns_import_project region for lib/ktbs/methods/hrules.py, which needs the
# same two bindings.
from rdflib import Namespace

KTBS_NS_URI = "http://liris.cnrs.fr/silex/2009/ktbs"
KTBS = Namespace(KTBS_NS_URI + "#")
__namespaces__ = {"ktbs": KTBS}
