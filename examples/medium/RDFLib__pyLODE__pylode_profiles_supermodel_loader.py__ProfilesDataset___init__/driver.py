"""Validation driver for ProfilesDataset.__init__.

The region is a constructor extracted from ``ProfilesDataset(Dataset)``.
The stub below plays ``self``: it provides the three sibling methods the
body calls (load_owl_imports, load_profiles, add_graph) and records what
they receive, so ``__eq__`` compares the *observable* outcome of the
constructor -- the base-class init kwargs, the tracked resources, and the
graphs handed to add_graph / load_profiles (by isomorphism).

Fixtures: data with two prof:Profile subjects (so the CBD extraction loop
runs and the remaining graph is non-empty) and data with none.
"""
from rdflib import BNode, Graph, URIRef
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair

WITH_PROFILES = """
@prefix prof:  <http://www.w3.org/ns/dx/prof/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/profile/a> a prof:Profile ;
    rdfs:label "Profile A" ;
    prof:hasResource [ dcterms:format "text/turtle" ] .

<http://example.org/profile/b> a prof:Profile ;
    rdfs:label "Profile B" .

<http://example.org/vocab/thing> a rdfs:Class ;
    rdfs:label "Thing" .
"""

NO_PROFILES = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.org/vocab/thing> a rdfs:Class ; rdfs:label "Thing" .
"""


def _digest(g):
    # anonymous graph names differ between the two runs by construction
    name = "_:anon" if isinstance(g.identifier, BNode) else str(g.identifier)
    return (name, to_isomorphic(g).graph_digest())


class _Dataset:
    """Stand-in for ProfilesDataset (the region's ``self``)."""

    def __init__(self):
        self.super_init_kwargs = None
        self.added = []
        self.loaded = []

    # sibling methods of the real class, stubbed
    def load_owl_imports(self, graph):
        return graph                       # no owl:imports in the fixtures

    def load_profiles(self, profiles_graph, graph):
        self.loaded.append((_digest(profiles_graph), _digest(graph)))

    def add_graph(self, graph):
        self.added.append(_digest(graph))

    def __eq__(self, other):
        return (isinstance(other, _Dataset)
                and self.super_init_kwargs == other.super_init_kwargs
                and getattr(self, "root_profile_iri", None)
                == getattr(other, "root_profile_iri", None)
                and getattr(self, "external_resources", None)
                == getattr(other, "external_resources", None)
                and getattr(self, "client", None) == getattr(other, "client", None)
                and self.added == other.added
                and self.loaded == other.loaded)

    def __repr__(self):
        return "_Dataset(added=%d, loaded=%d, super=%r)" % (
            len(self.added), len(self.loaded), self.super_init_kwargs)


def case(data):
    return lambda: ((_Dataset(), "http://example.org/profile/root", data), {})


VERDICT = run_pair(
    __file__,
    entry="__init__",
    calls=[case(WITH_PROFILES), case(NO_PROFILES)],
)
