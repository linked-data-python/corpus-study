# Extracted from senzing-garage/sz-semantics@bdefa5a738 : src/sz_semantics/sem.py
# region: Thesaurus.__init__ (lines 61-83, stratum ns_import_project)
# licence of the source repository: see meta.json
import logging
from rdflib.namespace import DC, DCAT, PROV, RDF, SKOS
import rdflib
from .util import KeyValueStore
from .namespace import SZ

def __init__(
    self,
    *,
    kv_store: KeyValueStore = KeyValueStore(),
) -> None:
    """
    Constructor.

    This expects the `load_source()` method will be used to load the taxonomy
    directly after constructing an instance.

    Note: override `KeyValueStore` to replace the Python built-in `dict` for
    larger scale such as [`rocksdict`](https://github.com/rocksdict/rocksdict).
    """
    self.logger = logging.getLogger(__name__)
    self.kv_store: KeyValueStore = kv_store

    self.rdf_graph: rdflib.Graph = rdflib.Graph(bind_namespaces="rdflib")
    self.rdf_graph.bind("dc", DC)
    self.rdf_graph.bind("dcat", DCAT)
    self.rdf_graph.bind("prov", PROV)
    self.rdf_graph.bind("skos", SKOS)
    self.rdf_graph.bind("sz", SZ)
