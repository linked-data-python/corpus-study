"""Validation driver for kumagallium__asterism__api_tests_test_orphan_reclaim_api.py___add_version.

Establishes semantic equivalence of original.py and translated.ldpy.
`_add_version(ds, iri)` returns nothing and writes into a named graph of
`ds`: the harness compares the `ds` argument after the call, through
`_DatasetHolder`, graph by graph (identifier -> isomorphism).

Calls:

  * call[0] -- the original single case: an empty Dataset, one IRI.
  * call[1], call[2] -- added by the mutation audit of 2026-10-30, in the
    shape the repository really uses (tests/test_orphan_reclaim_api.py:129-134
    and 153-159): `iri` is `substrate.versioned_graph_iri(...)`, a str of the
    form `https://kumagallium.github.io/asterism/graph/canonical/<id>/v<n>`,
    and `_add_version` is called on a Dataset that already holds another
    version graph (and, in call[2], the control-graph pointer that
    `_promote_pointer` writes). A translation that wrote into a fixed or
    stale named graph would leave call[0] green; here the two graphs must
    stay apart.
  * call[3] -- the same IRI as the graph already present: the write is
    idempotent, the graph keeps one triple.

The prefix bindings `@graph` adds to the dataset (`ex:`) are not compared:
the repository never serialises this Dataset as RDF -- it only answers
SPARQL SELECTs as JSON results (`_DatasetClient.sparql_select`), where no
prefix appears -- and nothing in the test binds `https://ex#` under
another prefix.
"""
import rdflib
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair

_EX = rdflib.Namespace("https://ex#")
_BASE = "https://kumagallium.github.io/asterism/graph/canonical/"
_CONTROL = rdflib.URIRef("https://kumagallium.github.io/asterism/graph/control")


class _DatasetHolder:
    """Wraps an ``rdflib.Dataset``: NOT a ``Graph`` subclass, so the harness
    falls through to ``__eq__`` instead of trying isomorphism on the whole
    (multi-context) dataset, which ``rdflib.compare.to_isomorphic`` cannot
    handle (it iterates quads, not triples). Every other attribute is the
    Dataset's own, so the region sees a real Dataset's interface."""

    def __init__(self):
        self.ds = rdflib.Dataset()

    def __getattr__(self, name):
        if name.startswith("__"):       # keep the harness's protocol probes
            raise AttributeError(name)  # (hasattr(x, "__iter__")) on the holder
        return getattr(self.ds, name)

    def __eq__(self, other):
        if not isinstance(other, _DatasetHolder):
            return NotImplemented
        a = {str(c.identifier): to_isomorphic(c)
             for c in self.ds.contexts() if len(c)}
        b = {str(c.identifier): to_isomorphic(c)
             for c in other.ds.contexts() if len(c)}
        return a == b

    def __repr__(self):
        return "_DatasetHolder(%r)" % sorted(
            (str(c.identifier), len(c)) for c in self.ds.contexts() if len(c))


def _with_versions(*iris, pointer=None):
    """A Dataset already holding the version graphs `_add_version` would have
    written for `iris` (plain rdflib, identical on both sides), plus the
    control triple of `_promote_pointer` when `pointer` is given."""
    h = _DatasetHolder()
    for iri in iris:
        h.ds.graph(rdflib.URIRef(iri)).add((_EX.s, _EX.p, rdflib.Literal(iri)))
    if pointer is not None:
        h.ds.graph(_CONTROL).add((
            rdflib.URIRef(_BASE + pointer[0]),
            rdflib.URIRef("https://kumagallium.github.io/asterism/ns#liveGraph"),
            rdflib.URIRef(pointer[1])))
    return h


VERDICT = run_pair(
    __file__,
    entry='_add_version',
    calls=[
        lambda: ((_DatasetHolder(), "http://example.org/g1"), {}),
        lambda: ((_with_versions(_BASE + "ghost/v1"), _BASE + "real/v2"), {}),
        lambda: ((_with_versions(_BASE + "demo-00000002/v1",
                                 pointer=("demo-00000002", _BASE + "demo-00000002/v1")),
                  _BASE + "demo-00000002/v2"), {}),
        lambda: ((_with_versions(_BASE + "ghost/v1"), _BASE + "ghost/v1"), {}),
    ],
)
