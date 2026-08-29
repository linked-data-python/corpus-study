# Context shim (see meta.json): the two bindings this region needs from
# ktbs/ktbs@4f9f50c770 : lib/ktbs/namespace.py -- KTBS_NS_URI (a plain
# string) and KTBS (a namespace object read via KTBS.hasTrace). The real
# namespace.py additionally imports `rdfrest.cores.local` and
# `rdfrest.util.helper_service` to build a REST description service around
# the vocabulary graph; `rdfrest` is not installed here (verified:
# ModuleNotFoundError) and none of that machinery is reached by this
# region -- only the two names below are. KTBS_NS_URI and the local name
# `hasTrace` are copied verbatim from the real file (namespace.py lines
# 39-40 for KTBS_NS_URI; `hasTrace` is a real fragment of the kTBS
# vocabulary, namespace.py's own embedded Turtle, `:hasTrace a
# owl:ObjectProperty ... rdfs:domain :Obsel`). The real KTBS is a
# rdflib.namespace.ClosedNamespace restricted to the vocabulary's own
# term set; a plain Namespace is used here since this region touches only
# one term and ClosedNamespace's closed-membership check is not part of
# what the region depends on.
from rdflib import Namespace

KTBS_NS_URI = "http://liris.cnrs.fr/silex/2009/ktbs"
KTBS = Namespace(KTBS_NS_URI + "#")
__namespaces__ = {"ktbs": KTBS}
