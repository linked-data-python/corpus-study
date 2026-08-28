# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/assets/make_builtin.py
# region: <module> (lines 1-35, band high)
# licence of the source repository: see meta.json
import pickle

from rdflib import Graph, URIRef
from rdflib.plugins.stores.memory import Memory

from pyshacl.monkey import apply_patches

apply_patches()
identifier = URIRef("http://datashapes.org/schema")
store = Memory(identifier=identifier)
with open("./schema.ttl", "rb") as f:
    g = Graph(store=store, identifier=identifier, bind_namespaces='core').parse(file=f)
with open("./schema.pickle", "wb") as f:
    pickle.dump((store, identifier), f, protocol=5)

identifier = URIRef("http://www.w3.org/ns/shacl#")
store = Memory(identifier=identifier)
with open("./shacl.ttl", "rb") as f:
    g = Graph(store=store, identifier=identifier, bind_namespaces='core').parse(file=f)
with open("./shacl.pickle", "wb") as f:
    pickle.dump((store, identifier), f, protocol=5)

identifier = URIRef("http://datashapes.org/dash")
store = Memory(identifier=identifier)
with open("./dash.ttl", "rb") as f:
    g = Graph(store=store, identifier=identifier, bind_namespaces='core').parse(file=f)
with open("./dash.pickle", "wb") as f:
    pickle.dump((store, identifier), f, protocol=5)

identifier = URIRef("http://www.w3.org/ns/shacl-shacl#")
store = Memory(identifier=identifier)
with open("./shacl-shacl.ttl", "rb") as f:
    g = Graph(store=store, identifier=identifier, bind_namespaces='core').parse(file=f)
with open("./shacl-shacl.pickle", "wb") as f:
    pickle.dump((store, identifier), f, protocol=5)

