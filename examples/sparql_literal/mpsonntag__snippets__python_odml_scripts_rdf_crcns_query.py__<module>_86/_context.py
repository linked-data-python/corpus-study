# Context shim (see meta.json): subset of the imports and NAMESPACE_MAP from
# python/odml/scripts/rdf_crcns_query.py in mpsonntag/snippets@164fac3966,
# so the region executes outside the script. ODML_NS is odml.format.Format._ns
# in odml.tools.rdf_converter (odml is not vendored here).
# Identical bindings for both representations.
from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery

ODML_NS = "https://g-node.org/odml-rdf#"
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}
