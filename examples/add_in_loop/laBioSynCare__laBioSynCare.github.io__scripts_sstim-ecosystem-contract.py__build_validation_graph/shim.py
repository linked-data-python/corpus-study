# Context shim (see meta.json): minimal stand-ins for the module-level names
# that scripts/sstim-ecosystem-contract.py defines elsewhere in the source
# repository (ROOT, MANIFEST_MODULES, FULL_PROFILE, ONTOLOGY_DIR, and the
# parse_graph helper that loads a list of Turtle files into one Graph), so
# the region executes outside the package. Identical bindings for both
# representations.
from pathlib import Path
from rdflib import Graph

HERE = Path(__file__).parent
ROOT = HERE / "context"
ONTOLOGY_DIR = HERE / "ontology"

MANIFEST_MODULES = {
    "module-a": {"source": {"path": "ctx-a.ttl"}},
}
FULL_PROFILE = {"modules": ["module-a"]}


def parse_graph(paths):
    g = Graph()
    for p in paths:
        g.parse(source=str(p), format="turtle")
    return g
