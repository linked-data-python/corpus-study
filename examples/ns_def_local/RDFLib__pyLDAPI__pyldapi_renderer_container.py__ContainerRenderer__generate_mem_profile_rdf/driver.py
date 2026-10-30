"""Validation driver for RDFLib__pyLDAPI__pyldapi_renderer_container.py__ContainerRenderer__generate_mem_profile_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is an unbound method (`def _generate_mem_profile_rdf(self): ...`),
so each call hands it a stand-in `self` carrying every attribute the body
reads: `instance_uri`, `label`, `comment`, `members`, `request.query_params`,
`per_page`, `page`, `last_page`, `parent_container_uri` and
`parent_container_label`.  The returned graph is compared by isomorphism.

PREFIX BINDINGS.  Isomorphism does not see them, yet the repository
serialises this graph (`_render_mem_profile_rdf` ->
`Renderer._make_rdf_response`), so `ldp:`/`xhv:` reach the response text.
The original binds them with `g.bind`; the translation through `@prefix`
plus `@graph g`.  `_bindings_lost` rebuilds the graph of every call on both
sides and requires every (prefix, namespace) the ORIGINAL graph binds to be
bound identically by the translated one; extra bindings are tolerated
(ldpy/027).  Its findings are merged into the single verdict `run_pair`
emits.

CALLS (one per way an input decides a triple; the real shapes come from
pyldapi/renderer_container.py: `members` is a list of URI strings, of
`{"uri", "title"}` dicts, of `(URI, label)` / `(URI, URI, label)` tuples of
str, or — ContainerOfContainersRenderer — of `(URIRef, Literal)` rows of a
SPARQL result, with `parent_container_uri`/`_label` None; `query_params` is
a starlette multi-dict, read by key):
  0. page 2 of 5, one member of each shape, a foreign query parameter, a
     parent container with a label: every island at least once;
  1. page 1 of 1: neither prev nor next; no parent; no member; no query
     parameter (the `other_qsas_str = ''` branch);
  2. page = last_page: prev but no next; a parent WITHOUT a label; `page`
     and `per_page` among the query parameters (filtered out) next to two
     kept ones;
  3. the ContainerOfContainersRenderer shape: SPARQL rows `(URIRef,
     Literal@en)` and `(URIRef, typed Literal)`, parent None;
  4. a three-element tuple (its member[1], a class URI string, is what the
     region labels with), a dict whose title is an int, label None and an
     int comment (coercion of non-str values on both sides);
  5. label and comment already Literals (a language-tagged one re-tagged
     @en, a typed one);
  6. a plain-string member whose text contains "uri": `"uri" in member` is a
     substring test, so the region indexes a str by "uri" and raises
     TypeError — compared by type and message on both sides.
"""
from types import SimpleNamespace

from rdflib import Literal, URIRef, XSD

from rdfeval import harness
from rdfeval.harness import run_pair


def _fake_container(**over):
    # types.SimpleNamespace (not a plain class) so the harness's own
    # arg[0]-after-the-call comparison (it checks the region did not mutate
    # what it was handed) has a working `==` to compare with: a plain class
    # instance would compare by identity and fail on two separate instances
    # even though neither side mutates it.
    attrs = dict(
        instance_uri="http://example.org/container/1",
        label="Container One",
        comment="A container of members.",
        members=[
            {"uri": "http://example.org/member/1", "title": "Member One"},
            ("http://example.org/member/2", "Member Two"),
            "http://example.org/member/3",
        ],
        query_params={"foo": "bar"},
        per_page=20,
        page=2,
        last_page=5,
        parent_container_uri="http://example.org/container/0",
        parent_container_label="Parent Container",
    )
    attrs.update(over)
    attrs["request"] = SimpleNamespace(query_params=attrs.pop("query_params"))
    return SimpleNamespace(**attrs)


CASES = [
    lambda: _fake_container(),
    lambda: _fake_container(members=[], query_params={}, page=1, last_page=1,
                            parent_container_uri=None,
                            parent_container_label=None),
    lambda: _fake_container(
        query_params={"page": "5", "per_page": "20", "a": "1", "b": "x-y"},
        page=5, last_page=5, parent_container_label=None),
    lambda: _fake_container(
        members=[(URIRef("http://example.org/reg/a"), Literal("Reg A", lang="en")),
                 (URIRef("http://example.org/reg/b"), Literal("7", datatype=XSD.integer))],
        query_params={}, page=1, last_page=1,
        parent_container_uri=None, parent_container_label=None),
    lambda: _fake_container(
        members=[("http://example.org/m/4", "http://example.org/Class", "Four"),
                 {"uri": "http://example.org/m/5", "title": 5}],
        label=None, comment=42),
    lambda: _fake_container(label=Literal("Conteneur", lang="fr"),
                            comment=Literal("3", datatype=XSD.integer)),
    lambda: _fake_container(members=["http://example.org/uri/9"]),
]


def _bindings_lost():
    """Prefix bindings an original graph carries and the translated one lacks."""
    here = harness.Path(__file__).resolve().parent
    ns_o, _ = harness._exec_python(here / "original.py")
    ns_t, _ = harness._exec_ldpy(here / "translated.ldpy")
    lost = []
    for i, make in enumerate(CASES):
        try:
            go = ns_o["_generate_mem_profile_rdf"](make())
            gt = ns_t["_generate_mem_profile_rdf"](make())
        except Exception:
            continue            # a raise is compared by run_pair itself
        got = {(p, str(n)) for p, n in gt.namespaces()}
        miss = sorted((p, str(n)) for p, n in go.namespaces()
                      if (p, str(n)) not in got)
        if miss:
            lost.append(f"call[{i}]: prefix bindings lost {miss}")
    return lost


_LOST = _bindings_lost()
_emit = harness._emit


def _emit_with_bindings(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _LOST
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _LOST
    _emit(verdict)


harness._emit = _emit_with_bindings

VERDICT = run_pair(
    __file__,
    entry='_generate_mem_profile_rdf',
    calls=[(lambda make=make: ((make(),), {})) for make in CASES],
)
