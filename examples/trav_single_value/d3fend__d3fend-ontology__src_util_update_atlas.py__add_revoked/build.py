# Context shim (see meta.json): subset of src/util/build.py from
# d3fend/d3fend-ontology@cce593d61c, so the region's `from build import
# get_graph, _xmlns` resolves outside the repository.  `PUBLIC_ONTOLOGY_FILEPATH`,
# `colors`, `log` and `get_graph` are copied verbatim.
#
# `_xmlns` is NOT defined in build.py at that commit (the real
# src/util/update_atlas.py raises ImportError there, as do update_attack.py and
# test_cases.py, which import it the same way).  It is restored here as the
# D3FEND ontology namespace, the one update_atlas.py itself binds as
# `d3fend = Namespace(".../d3fend.owl#")`, since the region builds technique IRIs
# with `URIRef(_XMLNS + atlas_id)`.  Identical bindings for both representations.
from rdflib import Graph

PUBLIC_ONTOLOGY_FILEPATH = "build/d3fend-public-with-controls.ttl"

_xmlns = "http://d3fend.mitre.org/ontologies/d3fend.owl#"


class colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def log(message, error=False, info=False):
    if error:
        print(colors.FAIL + message)
    elif info:
        print(colors.OKBLUE + message)
    else:
        print(colors.OKGREEN + message)


def get_graph(filename=PUBLIC_ONTOLOGY_FILEPATH):
    g = Graph()
    g.parse(filename)
    log(filename)
    log(f"The graph has {len(g)} triples", info=True)
    return g
