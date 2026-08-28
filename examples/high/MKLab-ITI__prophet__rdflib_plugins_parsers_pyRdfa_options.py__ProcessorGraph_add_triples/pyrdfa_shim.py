# Context shim (see meta.json): the namespace objects options.py imports from
# its package, copied verbatim from MKLab-ITI/prophet@eee2ab51de
# rdflib/plugins/parsers/pyRdfa/__init__.py (lines 200-212), plus the three
# processor-graph classes used as realistic top_class/info_class values by
# driver.py (lines 255-257).  Identical for both representations.
from rdflib import Namespace

ns_rdfa = Namespace("http://www.w3.org/ns/rdfa#")
ns_xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
ns_distill = Namespace("http://www.w3.org/2007/08/pyRdfa/vocab#")

RDFA_Error = ns_rdfa["Error"]
RDFA_Warning = ns_rdfa["Warning"]
RDFA_Info = ns_rdfa["Information"]
