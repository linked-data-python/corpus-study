"""Validation driver for SoftwareHeritage__swh-indexer__swh_indexer_metadata_mapping_github.py__GitHubMapping_translate_parent.

Establishes semantic equivalence of original.py and translated.ldpy.
translate_parent(self, graph, root, v) mutates `graph` in place and returns
None; `self` is unused by the region's own body (no method on it is called),
so a bare None stands in for it. Each case is a callable so a fresh Graph()
and BNode() are built per side -- the harness invokes `case()` once per
version, and mutable arguments must not leak across the two runs.

Repository shape (calls 3-4): in swh-indexer, BaseMapping._translate_dict
(metadata_mapping/base.py:250-252) passes root = self.get_root_uri(...),
which GitHubMapping (github.py:57-59) makes a URIRef of the repository's
html_url, and _translate_to_graph (base.py:291) has already added
(root, rdf:type, schema:SoftwareSourceCode) before dispatching to
translate_parent (base.py:300). With a bare BNode root on an empty graph,
the subject of the added triple is indistinguishable from a fresh blank node
under isomorphism; the pre-existing triple on the same root makes the
subject observable (mutant `+{ [] ... }` is killed by calls 3 and 4).

Guard values (calls 5-8): the guard is `isinstance(v.get("html_url"), str)`,
not a truthiness or `is not None` test. An empty string is a str and is
written as URIRef(""); None (GitHub's JSON null) and a non-str value are
skipped. These kill the mutants `if v.get("html_url")` (call 5) and
`if v.get("html_url") is not None` (calls 7-8).
"""
from rdfeval.harness import run_pair
from rdflib import RDF, BNode, Graph, Namespace, URIRef

SCHEMA = Namespace("http://schema.org/")
FORK = URIRef("https://github.com/someone/fork-of-software")


def _repo_graph(root):
    """The graph as _translate_to_graph hands it over (base.py:291)."""
    g = Graph()
    g.add((root, RDF.type, SCHEMA.SoftwareSourceCode))
    return g


def _repo_case(v, root_factory=lambda: FORK):
    def case():
        root = root_factory()
        return ((None, _repo_graph(root), root, v), {})
    return case


VERDICT = run_pair(
    __file__,
    entry='translate_parent',
    calls=[
        # 0. html_url present: the guarded triple is added.
        lambda: ((None, Graph(), BNode(),
                  {"html_url": "http://example.org/test-software"}), {}),
        # 1. html_url absent: isinstance(v.get("html_url"), str) is False, no
        # triple is added -- exercises the guard, not just the add.
        lambda: ((None, Graph(), BNode(), {"other_field": "x"}), {}),
        # 2. v is not a dict at all: the isinstance(v, dict) guard short-circuits.
        lambda: ((None, Graph(), BNode(), "not-a-dict"), {}),
        # 3. repository shape: URIRef root already typed SoftwareSourceCode,
        # v as GitHub's API "parent" object.
        _repo_case({"html_url": "https://github.com/someone/software",
                    "full_name": "someone/software"}),
        # 4. BNode root (the annotated type) on a graph that already says
        # something about it: the new triple must hang off the same node.
        _repo_case({"html_url": "https://github.com/someone/software"},
                   root_factory=BNode),
        # 5. html_url == "": falsy but a str -> URIRef("") is written.
        _repo_case({"html_url": ""}),
        # 6. html_url is JSON null -> skipped.
        _repo_case({"html_url": None}),
        # 7. html_url is a non-str, non-None value -> skipped (URIRef(42)
        # would raise).
        _repo_case({"html_url": 42}),
        # 8. html_url is a nested object -> skipped.
        _repo_case({"html_url": {"href": "https://github.com/x/y"}}),
    ],
)
