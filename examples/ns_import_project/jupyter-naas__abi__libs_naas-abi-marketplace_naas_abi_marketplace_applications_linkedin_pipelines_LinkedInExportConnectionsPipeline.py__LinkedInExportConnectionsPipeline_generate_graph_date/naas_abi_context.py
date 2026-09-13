# Context shim (see meta.json): the three Namespace objects from
# naas_abi_core/utils/Graph.py, jupyter-naas/abi@3fb7f5304d, so the region
# executes outside the package (naas_abi_core is not installed here).
# Identical bindings for both representations; transcribed verbatim.
from rdflib import Namespace

BFO = Namespace("http://purl.obolibrary.org/obo/")
ABI = Namespace("http://ontology.naas.ai/abi/")
CCO = Namespace("https://www.commoncoreontologies.org/")

__namespaces__ = {"abi": ABI, "bfo": BFO, "cco": CCO}
