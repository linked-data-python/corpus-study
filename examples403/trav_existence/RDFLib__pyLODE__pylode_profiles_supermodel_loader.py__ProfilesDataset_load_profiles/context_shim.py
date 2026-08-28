# Context shim (see meta.json): the LODE namespace (from
# pylode/profiles/supermodel/namespace.py) and stand-ins for the
# httpx-backed `fetch` helper and the ProfilesDataset instance
# (pylode/profiles/supermodel/loader.py), from RDFLib/pyLODE@0d0471fb99, so
# the region executes outside its package and without performing real
# network I/O. Identical bindings for both representations.
import sys

from rdflib import Graph, Namespace

LODE = Namespace("https://w3id.org/lode/ns/pylode/")

# Canned remote artifacts: the real `fetch` performs an httpx GET keyed by
# URL and Accept header. Same (url, mediatype) in, same (data, content_type)
# out, no network -- this is data, not logic invented for the region.
_REMOTE = {
    "http://example.org/artifacts/other.ttl": (
        "@prefix ex: <http://example.org/> .\n"
        "ex:otherThing a ex:Widget .\n",
        "text/turtle",
    ),
    "http://example.org/artifacts/nested-profile.ttl": (
        "@prefix ex: <http://example.org/> .\n"
        "@prefix prof: <http://www.w3.org/ns/dx/prof/> .\n"
        "ex:nestedProfile a prof:Profile .\n",
        "text/turtle",
    ),
}


def fetch(url, client, content_type="text/turtle"):
    return _REMOTE[str(url)]


class Loader:
    """Stand-in for the `ProfilesDataset` instance `load_profiles` runs as a
    method of. Provides only what the region touches: `client`, `get_graph`,
    `add_graph`, `load_owl_imports`, and a `load_profiles` that re-enters
    whichever module (original.py or translated.ldpy) is currently calling
    it, so the region's own recursive `self.load_profiles(...)` stays inside
    the implementation under test rather than some third copy.
    """

    def __init__(self):
        self.client = None
        self.added = []
        self._named = {}

    def get_graph(self, identifier):
        return self._named.setdefault(
            str(identifier), Graph(identifier=str(identifier))
        )

    def add_graph(self, graph):
        self.added.append(graph)

    def load_owl_imports(self, graph):
        return graph  # no owl:imports triples in the fixture: identity holds

    def load_profiles(self, graph, prev_graph):
        caller_globals = sys._getframe(1).f_globals
        return caller_globals["load_profiles"](self, graph, prev_graph)
