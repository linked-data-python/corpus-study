# Extracted from mpsonntag/snippets@164fac3966 : python/odml/examples/example_rdf_query.py
# region: <module> (lines 17-23, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Namespace, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
# Context shim: ODML_NS lived in odml.tools.rdf_converter; restoring the
# binding so the region executes standalone (see shim.py).
from shim import ODML_NS
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}

q = prepareQuery("""SELECT *
            WHERE {
               ?d rdf:type odml:Document .
               ?d odml:hasSection ?s .
               ?s rdf:type odml:Section .
               ?s odml:hasType "setup/daq" .
            }""", initNs=NAMESPACE_MAP)
