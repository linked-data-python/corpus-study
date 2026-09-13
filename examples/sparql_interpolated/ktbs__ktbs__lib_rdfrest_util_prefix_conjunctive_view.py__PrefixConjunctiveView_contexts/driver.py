"""Validation driver for
ktbs__ktbs__lib_rdfrest_util_prefix_conjunctive_view.py__PrefixConjunctiveView_contexts.

IDENTITY translation (see meta.json): `contexts` assembles its query from
two runtime pieces neither of which is a term:

  * `self._filter` (set in `__init__`, restored here to its real shape --
    ``FILTER STRSTARTS(STR(?g), "prefix")``) is spliced straight after the
    `GRAPH ?g { ... }` block. It is an opaque SPARQL fragment, not a value:
    `s{ }`'s `{expr}` only stands where a TERM may stand (querying.md), and
    there is no island for "a filter clause held in a variable".
  * when `triple` is given, `inner_where = "%s %s %s" % tuple(i.n3() for i
    in triple)` builds a WHOLE triple PATTERN from data received as an
    argument -- the same limit INSTRUCTIONS.md SS2 notes for `-{ }`/`m{ }`
    (a WRITTEN pattern only, never one received as data), here on rdflib's
    own query engine.

Both are compile-time-fixed in the source's own comment ("the right thing
to do would be initBindings[...] but this would not work with Virtuoso"):
the author already tried the term-interpolation shape this stratum expects
and rejected it for a different reason (Virtuoso), landing on textual
splicing instead.

`contexts` is a generator method on `PrefixConjunctiveView` (a
`ConjunctiveGraph` subclass); executing it needs only `self.store`,
`self._whole` and `self._filter` (restored below as a minimal stand-in --
not `rdfrest`/ktbs specific, so no shim module is warranted), not the whole
resource-store machinery `lib/ktbs/engine/trace.py`'s `post_graph` (its
sibling in this batch) depends on.
"""
from rdflib import ConjunctiveGraph, Literal, Namespace, URIRef

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")
KEEP_1 = URIRef("http://example.org/graphs/keep-1")
KEEP_2 = URIRef("http://example.org/graphs/keep-2")
SKIP_1 = URIRef("http://example.org/graphs/skip-1")


class _View:
    """Minimal stand-in for PrefixConjunctiveView: only the three attributes
    `contexts` reads (`store`, `_whole`, `_filter`) -- see module docstring.

    `contexts` receives `self` as its first argument, and run_pair compares
    every argument between the two sides (a fresh instance built once per
    side, per call.py:1's "fresh mutable arguments" rule). Two distinct
    `_View` instances are never `==` under default identity, which would
    fail the pair on the fixture object itself rather than on what
    `contexts` actually computes from it -- so equality here means "same
    fixture shape", which is all this comparison should be judging.
    """

    def __eq__(self, other):
        return isinstance(other, _View)

    def __hash__(self):
        return 0


def _make_self():
    whole = ConjunctiveGraph()
    # Two contexts share a triple and match the prefix filter; a third
    # matches neither (wrong prefix and different triple) -- the "neighbour
    # that must not match" INSTRUCTIONS.md SS3 asks for.
    whole.get_context(KEEP_1).add((EX.s1, EX.p1, EX.o1))
    whole.get_context(KEEP_2).add((EX.s1, EX.p1, EX.o1))
    whole.get_context(SKIP_1).add((EX.s2, EX.p2, EX.o2))
    self_ = _View()
    self_.store = whole.store
    self_._whole = whole
    self_._filter = 'FILTER STRSTARTS(STR(?g),' + Literal("http://example.org/graphs/keep").n3() + ')'
    return self_


def _call(*call_args):
    # A fresh store per call, and per side (run_pair invokes this twice per
    # entry in `calls`), so no mutation on one side can leak into the
    # other's input.
    return lambda: ((_make_self(), *call_args), {})


VERDICT = run_pair(
    __file__,
    entry='contexts',
    calls=[
        _call(),                              # no triple: both kept contexts
        _call((EX.s1, EX.p1, EX.o1)),          # matching triple, prefix ok
        _call((EX.s2, EX.p2, EX.o2)),          # zero-solution case
    ],
    ordered=False,
)
