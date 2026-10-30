"""Validation driver for alganet__apysource__apysource_yaml_input.py___emit_cite_sites.

Establishes semantic equivalence of original.py and translated.ldpy.

The region mutates `g` in place and can raise half way through its loop, so
the harness compares three things for every call: the graph left behind
(partial, when the call raised), the return value, and the exception (same
type, same message).  What each call exercises:

Success paths
  multi_sites        two sites, one with a line and one without: the loop over
                     more than one row and the conditional `sv:citingLine`.
  no_cited_by        no `cited_by` key at all: nothing is emitted.
  cited_by_none      `cited_by: null`: same early return.
  empty_list         `cited_by: []`: a falsy list that is NOT refused, and
                     emits nothing.
  line_zero          `line: 0`: a falsy line that must still be emitted
                     (`is not None`, not truthiness).
  file_not_a_string  `file: 42` and `file: true`: `_text` accepts a number or
                     a boolean and the literal is its string.
  prefilled_graph    a graph that already holds a triple: the region only adds.
  numbering          a graph that already holds a marker on the blank node the
                     second site is numbered to (`cite_2`), so that the
                     numbering of the sites, which graph isomorphism alone
                     cannot see, changes the graph.

Error paths (each is a different raise of the original)
  not_a_list         `cited_by` is a mapping, then `""`, then `0`: refused as
                     "not a list", the falsy ones included.
  site_not_a_dict    the second site is a bare string; the first one has
                     already been written.
  unknown_key        one unknown key (singular message) and two (plural).
  no_file            `{}`, `file: ""` and `file: 0`: each is the "must name the
                     file" refusal, raised before anything is written.
  file_not_text      `file: ["x"]` as the SECOND site: `_text` raises after the
                     original has already added `(node, a, sv:CiteSite)`, so
                     the partial graph tells the order of the writes apart.
  line_not_int       `line: true`, `line: "12"`, `line: 1.5`: refused after the
                     three or four triples of the site are written.

The first version of translated.ldpy failed `file_not_text` ("5 vs 4 triples"):
it computed the file literal before writing the type triple, so it raised
with one triple fewer than the original.  Mutants of the corrected translation
that were run and rejected: `line is not None` -> `line` / `True`; `not file` ->
`file is None`; `not isinstance(sites, list)` -> `not sites` / `sites and ...`;
`sites is None` -> `not sites`; the site type check and the unknown-key check
removed; the bool exclusion of `line` removed; `int` widened to `float`;
numbering `i`, `i - 1`, `i + 1`; `enumerate(sites, 1)` -> `enumerate(sites)`;
the type triple removed; `sv:citedBy` reversed; `prov:wasDerivedFrom` aimed at
the site; `sv:citingLine` on the fragment; `Literal(line)` -> `Literal(str(line))`;
`_text(file, ...)` -> `file` / `str(file)`.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair
from apysource_shim import _anon

FRAG_URI = URIRef("https://alganet.github.io/apysource/example#frag-1")
WHAT = "example fragment"


def _call(frag_def, graph=None):
    def make():
        return (graph() if graph else Graph(), FRAG_URI, frag_def, WHAT), {}
    return make


def _prefilled():
    g = Graph()
    g.add((FRAG_URI, URIRef("http://purl.org/dc/terms/title"), Literal("kept")))
    return g


def _marked():
    # The graph already holds a marker on the node the SECOND site will get
    # (`_anon(frag, "cite_2")`): a blank node's label is invisible to graph
    # isomorphism unless something else in the graph carries the same label,
    # so this is what makes the numbering of the sites observable.
    g = Graph()
    g.add((_anon(FRAG_URI, "cite_2"), URIRef("http://example.org/marker"), Literal("second")))
    return g


def _sites(*sites):
    return {"cited_by": list(sites)}


GOOD = {"file": "src/ok.py", "line": 3}

CALLS = [
    # success paths
    _call(_sites({"file": "src/a.py", "line": 12}, {"file": "src/b.py"})),  # multi_sites
    _call({}),                                                              # no_cited_by
    _call({"cited_by": None}),                                              # cited_by_none
    _call({"cited_by": []}),                                                # empty_list
    _call(_sites({"file": "src/z.py", "line": 0})),                         # line_zero
    _call(_sites({"file": 42}, {"file": True})),                            # file_not_a_string
    _call(_sites({"file": "src/p.py"}), graph=_prefilled),                  # prefilled_graph
    _call(_sites({"file": "src/a.py", "line": 7}, {"file": "src/b.py"}), graph=_marked),  # numbering
    # error paths
    _call({"cited_by": {"file": "src/a.py"}}),                              # not_a_list: mapping
    _call({"cited_by": ""}),                                                # not_a_list: ""
    _call({"cited_by": 0}),                                                 # not_a_list: 0
    _call(_sites(GOOD, "src/x.py")),                                        # site_not_a_dict
    _call(_sites({"file": "src/a.py", "colour": "red"})),                   # unknown_key (one)
    _call(_sites(GOOD, {"file": "src/a.py", "colour": "red", "bar": 1})),   # unknown_key (two)
    _call(_sites({})),                                                      # no_file: absent
    _call(_sites(GOOD, {"file": ""})),                                      # no_file: ""
    _call(_sites({"file": 0})),                                             # no_file: 0
    _call(_sites({"file": "src/ok.py"}, {"file": ["x"]})),                  # file_not_text
    _call(_sites({"file": "src/a.py", "line": True})),                      # line_not_int: bool
    _call(_sites({"file": "src/a.py", "line": "12"})),                      # line_not_int: str
    _call(_sites(GOOD, {"file": "src/a.py", "line": 1.5})),                 # line_not_int: float
]

VERDICT = run_pair(
    __file__,
    entry='_emit_cite_sites',
    calls=CALLS,
)
