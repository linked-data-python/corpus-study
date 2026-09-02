# Context shim (see meta.json): the module-level namespace bindings and the
# `ProcessorGraph` wrapper class that
# LexMalta/recipes@b861b7ccea : recipe-importer/pyRdfa/options.py defines
# around `add_triples` (verified against that commit's options.py and
# __init__.py) -- this extraction's context window carries only the
# function body, not the package `from . import ns_xsd, ns_distill,
# ns_rdfa`, the local `ns_dc`/`ns_ht` `Namespace(...)` calls, `ns_rdf`
# (imported as `from rdflib import RDF as ns_rdf` at the top of
# options.py), or the class whose `__init__` sets `self.graph = Graph()`.
# Identical bindings for both representations.
from rdflib import Graph, Namespace
from rdflib import RDF as ns_rdf

ns_xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
ns_distill = Namespace("http://www.w3.org/2007/08/pyRdfa/vocab#")
ns_rdfa = Namespace("http://www.w3.org/ns/rdfa#")


class ProcessorGraph:
    """Wrapper around the 'processor graph' (options.py lines 43-49)."""

    def __init__(self):
        self.graph = Graph()
