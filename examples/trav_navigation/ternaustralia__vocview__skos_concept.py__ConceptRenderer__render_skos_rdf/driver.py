"""Validation driver for ternaustralia__vocview__skos_concept.py__ConceptRenderer__render_skos_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed once into `config.Config.g` (see
config.py), which the region only reads.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Added by the 2026-10-31 mutation audit:

- the four RDF media types the repository can actually pass as
  `self.format` (pyldapi's RDF_MEDIATYPES: text/turtle, application/rdf+xml,
  application/ld+json, application/n-triples), each through `render`, so the
  triples are compared in every serialisation the endpoint serves;
- a comparison of what `render`'s graph comparison cannot see: the
  Response's mimetype, and the prefix bindings the serialised body declares.
  `@graph g` binds the block's prefixes into `g` (record ldpy/027), and `g`
  is what the region serialises, so a prefix declared in the block would
  change the body.  Every binding the original's body declares must be in
  the translation's (extra ones are tolerated, AGENT_REPAIR.md).  The fixture
  carries a schema.org triple under http://, which rdflib's default
  `schema:` (https://) does not cover: it is the case where a block-level
  `@prefix schema: <http://schema.org/>` would rename the prefix the
  original emits.  This check runs after `run_pair` and is merged into its
  single RDFEVAL-VERDICT line, the only one `rdfeval check` reads.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _exec_artefact, run_pair, sides_from_env

HERE = Path(__file__).resolve().parent
MEDIA_TYPES = ["text/turtle", "application/rdf+xml", "application/ld+json",
               "application/n-triples"]

# The region reads a module global (config.Config.g), not a parameter, and
# its entry point (`_render_skos_rdf`) takes a `self` rather than a graph --
# so this driver calls the `render(uri, fmt)` test wrapper instead of using
# fixture= (which would pass a freshly-parsed graph as the sole argument).
# fixture.ttl is still the input graph: config.py (the context shim) parses
# it once into Config.g -- see its header for why sharing that one parse
# between the two sides is safe here (the region only reads it).
_stderr = io.StringIO()
with contextlib.redirect_stderr(_stderr):
    VERDICT = run_pair(
        __file__,
        entry='render',
        calls=[
            lambda: (("http://example.org/concept1", "turtle"), {}),  # several
            # solutions plus a blank-node object whose own triples must be
            # pulled in too
            lambda: (("http://example.org/concept2", "turtle"), {}),  # the
            # neighbourhood, rendered on its own: concept1's triples must not
            # leak in either direction
            lambda: (("http://example.org/absent", "turtle"), {}),  # zero
            # solutions: not a subject of anything in the fixture
        ] + [
            # the media types the repository really serves (audit 2026-10-31)
            (lambda fmt=fmt: (("http://example.org/concept1", fmt), {}))
            for fmt in MEDIA_TYPES
        ],
    )


def _rendered(artefact, name):
    """mimetype and declared prefixes of every rendering, for one side."""
    sys.modules.pop("config", None)      # a fresh Config.g for each side
    ns, _ = _exec_artefact(HERE / artefact, name)
    out = {}
    for uri in ("http://example.org/concept1", "http://example.org/absent"):
        for fmt in MEDIA_TYPES:
            resp = ns["_render_skos_rdf"](ns["_FakeConceptRenderer"](uri, fmt))
            body = Graph(bind_namespaces="none").parse(
                data=resp.get_data(as_text=True), format=fmt)
            out[f"{uri} {fmt}"] = (resp.mimetype,
                                   {(p, str(n)) for p, n in body.namespaces()})
    return out


try:
    _left, _right = sides_from_env()
    _o = _rendered(_left, "__original_bindings__")
    _t = _rendered(_right, "__translated_bindings__")
    for _key in sorted(_o):
        (_mo, _bo), (_mt, _bt) = _o[_key], _t[_key]
        if _mo != _mt:
            VERDICT["diffs"].append(f"{_key}: mimetype differs ({_mo!r} vs {_mt!r})")
        if not _bo <= _bt:
            VERDICT["diffs"].append(f"{_key}: prefix bindings of the original "
                                    f"missing from the translation: {sorted(_bo - _bt)}")
    VERDICT["bindings_compared"] = len(_o)
except Exception as _e:                  # noqa: BLE001 - reported in the verdict
    VERDICT["diffs"].append(f"bindings check: {type(_e).__name__}: {_e}")
VERDICT["equivalent"] = not VERDICT["diffs"] and not VERDICT.get("error")

for _line in _stderr.getvalue().splitlines():
    if not _line.startswith("RDFEVAL-VERDICT "):
        print(_line, file=sys.stderr)
print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)
