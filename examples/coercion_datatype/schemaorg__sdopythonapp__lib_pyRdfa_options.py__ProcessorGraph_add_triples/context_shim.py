# Context shim (see meta.json): the four namespaces original.py takes from the
# package __init__ (`from . import ns_xsd, ns_distill, ns_rdfa`, plus `ns_rdf`
# which the region also uses), so the region executes outside the package.
# From schemaorg/sdopythonapp@128be97d35 : lib/pyRdfa/__init__.py, same IRIs.
# Identical bindings for both representations.
from rdflib import Namespace

ns_rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ns_xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
ns_distill = Namespace("http://www.w3.org/2007/08/pyRdfa/vocab#")
ns_rdfa = Namespace("http://www.w3.org/ns/rdfa#")
