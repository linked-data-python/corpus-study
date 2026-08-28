# Context shim (see meta.json): the bindings the region imports from the
# pyRdfa package of MKLab-ITI/prophet@eee2ab51de
# (rdflib/plugins/parsers/pyRdfa/__init__.py, lines 200, 259/261 and 288/289),
# so that the region executes outside the package.
# Used IDENTICALLY by original.py and translated.ldpy.
from rdflib import Namespace

ns_rdfa = Namespace("http://www.w3.org/ns/rdfa#")

UnresolvablePrefix = ns_rdfa["UnresolvedCURIE"]
UnresolvableTerm = ns_rdfa["UnresolvedTerm"]

err_illegal_safe_CURIE = "Illegal safe CURIE: %s; ignored"
err_no_CURIE_in_safe_CURIE = (
    "Safe CURIE is used, but the value does not correspond to a defined "
    "CURIE: [%s]; ignored"
)
