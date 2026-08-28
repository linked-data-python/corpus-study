# Context shim (see meta.json): the three namespace objects the region imports
# with `from . import ns_xsd, ns_distill, ns_rdfa`, copied verbatim from
# rdflib/plugins/parsers/pyRdfa/__init__.py (lines 200-212) of
# MKLab-ITI/prophet@eee2ab51de.  A local module is used rather than the corpus
# checkout because that checkout vendors a whole old rdflib package, which on
# sys.path would shadow the installed one.
# Identical for both representations.
from rdflib	import Namespace

ns_rdfa		= Namespace("http://www.w3.org/ns/rdfa#")
ns_xsd		= Namespace('http://www.w3.org/2001/XMLSchema#')
ns_distill	= Namespace("http://www.w3.org/2007/08/pyRdfa/vocab#")
