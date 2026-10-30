"""Validation driver for BrickSchema__Brick__generate_brick.py__define_shape_property_property.

This region READS a graph (the `optional and no other keys` branch queries
the current graph for an existing, unconstrained sh:PropertyShape) and also
WRITES to it, so the oracle is the equality of the graph mutated by each
side from the same input graph (design record corpus/405), plus whatever the
call returns.  `fixture.ttl` is parsed fresh for each side.

The entry point does not take a lone graph argument — its signature is
`define_shape_property_property(shape_name, definitions, graph=...)` — so
`calls=` supplies shape_name/definitions explicitly and passes the freshly
parsed fixture as the `graph` keyword; `run_pair` compares that kwarg after
the call (graph isomorphism) exactly as it would a positional `graph=`
argument taken from `fixture=`.

`definitions` is exercised across every branch the region has:
  - "or": a nested recursive definition (sh:or + rdf:Collection)
  - optional + no other key, existing shape found -> reuse (read via s{ })
  - optional + no other key, existing shape NOT found -> create new
  - datatype (plain) -> sh:datatype
  - datatype == BSH.NumericValue -> sh:or bsh:NumericValue
  - values -> sh:in + rdf:Collection
`definitions` is mutated in place (.pop) by the region, so the call is a
fresh callable invoked once per side.

STRENGTHENED (repair 2026-10-30).  Three things the first driver hid:

  * the shim's `add_relationships` was a no-op, so the last line of the
    region wrote nothing.  The real function (generate_brick.py:85-91) is
    restored verbatim by `_add_relationships` below and installed on
    `context_shim` before the artefacts are loaded, so both sides call it.
    The repository's real calls leave keys in `definitions` for it
    (bricksrc/entity_properties.py: skos:definition, sh:minCount,
    sh:maxCount, sh:class), and a leftover `values` key next to a datatype
    makes it raise (a str is not a predicate), which is an error path the
    harness compares;
  * the `import_from` branch was never taken.  The repository never passes
    that key (it occurs only in the definition), but it is the only place
    where the term-position interpolation of the second `s{ }` (`{prop_name}`
    in subject position) is observable, so calls 11-14 take it, with a local
    Turtle file (`import_from.ttl`) whose objects are falsy, tagged, typed,
    blank and IRI terms, and with a missing file;
  * the first `s{ }` (the reuse lookup, `SELECT ?x { ?p sh:property ?p … }`)
    can NEVER return a row: `?x` is not bound by the pattern, and rdflib
    7.2.1 returns an empty result for an unbound projected variable even
    when a reflexive `ex:s sh:property ex:s ; sh:path ex:hasWindow` exists
    (ran: `SELECT ?p` with the same pattern returns that row, `SELECT ?x`
    returns []).  Besides, the repository only writes `optional` together
    with other keys, so that branch's guard is never true there.  Calls 6-9
    and 19 still reach the query (an optional property alone, its
    neighbours optional False / optional with a second key / no optional,
    and the reflexive shapes of fixture.ttl, one of them min- and one
    max-constrained) and compare what follows.  The interpolation
    `{prop_name}` of this query cannot be observed by any input: a mutant
    of it (`?p sh:path ?zz`, FILTER(1 = 2), the FILTER lines removed) stays
    green, being equivalent on a query that returns nothing.  What the
    driver does prove is that the translation kept the query dead (the
    mutant `SELECT ?p` is rejected by call 19).  Proof that the
    interpolation itself is right, run once in a copy of this directory
    with `SELECT ?x` changed to `SELECT ?p` in BOTH original.py and
    translated.ldpy: the pair stays OK, and translation mutants
    `?p sh:path ?zz`, each FILTER NOT EXISTS replaced by FILTER(1 = 2) or
    removed are all rejected.

CALLS (fixture.ttl is parsed fresh for each side; `_call` builds the
arguments):
  0   the original call: or / optional alone (existing and unmatched shape)
      / datatype / NumericValue / values;
  1-2 repository shapes: LastKnownValueShape (datatype on a property,
      sh:minCount/sh:maxCount keys left to add_relationships) and a
      deprecation shape (skos:definition literal, sh:class, optional True
      with other keys, optional False with a key);
  3-4 `values` as the repository writes them: [1, 2, 3, "Total"] (ints and
      str), and falsy members ([0, ""]) plus the empty list;
  5   leftover keys: a list value (also empty), a falsy Literal(0), a
      dict-valued key that add_relationships must skip;
  6-9 the reuse lookup's guard, each term false in turn (see above);
  10  `or`: nested two levels, an empty `or` list, and `or` beside plain
      properties;
  11-14 `import_from`: copied terms (falsy, tagged, typed, blank, IRI),
      a property with no triple in the file (zero rows), import with
      optional False and with a datatype, a missing file (raise);
  19  the reuse lookup on reflexive shapes (fixture.ttl): never reused;
  15-18 error paths: a property definition that is None, `or` that is not
      iterable, a leftover `values` key beside a datatype (AssertionError
      from graph.add in add_relationships), a leftover str key.
"""
from pathlib import Path

from rdflib import URIRef, Literal
from rdflib.namespace import Namespace, SKOS, SH

from rdfeval.harness import run_pair, fixture_graph

import context_shim

EX = Namespace("http://example.org/")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

_HERE = Path(__file__).resolve().parent
_FIXTURE = _HERE / "fixture.ttl"
_IMPORT = str(_HERE / "import_from.ttl")


def _add_relationships(item, propdefs, graph=None):
    # generate_brick.py:85-91, verbatim (default argument aside: every call
    # of the region passes graph=).
    for propname, propval in propdefs.items():
        if isinstance(propval, list):
            for pv in propval:
                graph.add((item, propname, pv))
        elif not isinstance(propval, dict):
            graph.add((item, propname, propval))


# Both artefacts do `from context_shim import add_relationships` when they
# are executed, after this line: the shim's no-op is replaced for both.
context_shim.add_relationships = _add_relationships


def _call(shape_name, make_definitions):
    """A case: a fresh graph and fresh definitions (the region pops keys)."""
    def build():
        return ((shape_name, make_definitions()),
                {"graph": fixture_graph(_FIXTURE)})
    return build


CALLS = [
    # 0 -- the original call
    _call(EX.MainShape, lambda: {
        "or": [{EX.hasSubArea: {"datatype": XSD.string}}],
        EX.hasWindow: {"optional": True},
        EX.hasTag: {"optional": True},
        EX.hasColor: {"datatype": XSD.string},
        EX.hasWeight: {"datatype": BSH.NumericValue},
        EX.hasStatus: {"values": ["open", "closed"]},
    }),
    # 1 -- LastKnownValueShape as bricksrc/entity_properties.py writes it
    _call(BSH.LastKnownValueShape, lambda: {
        BRICK.timestamp: {"datatype": XSD.dateTime},
        BRICK.value: {SH.minCount: Literal(1), SH.maxCount: Literal(1)},
    }),
    # 2 -- deprecation shape: definitions, sh:class, optional with a key
    _call(BSH.DeprecationShape, lambda: {
        BRICK.deprecationMitigationMessage: {
            SKOS.definition: Literal("A message"), "datatype": XSD.string},
        BRICK.deprecationMitigationRule: {
            SKOS.definition: Literal("A rule"), SH["class"]: SH.NodeShape,
            "optional": True},
        BRICK.deprecationReason: {
            SKOS.definition: Literal("Why"), "optional": False},
    }),
    # 3 -- values as the repository writes them (ints and str)
    _call(BSH.PhaseCountShape, lambda: {
        BRICK.phaseCount: {"values": [1, 2, 3, "Total"]}}),
    # 4 -- falsy members, and an empty list
    _call(BSH.FalsyShape, lambda: {
        BRICK.zeroOrEmpty: {"values": [0, ""]},
        BRICK.noValues: {"values": []}}),
    # 5 -- leftover keys for add_relationships
    _call(BSH.LeftoverShape, lambda: {
        EX.hasLeft: {
            SKOS.definition: [Literal("a"), Literal("b")],
            SKOS.note: [],
            SKOS.scopeNote: Literal(0),
            SKOS.editorialNote: {"skipped": "dict value"},
        }}),
    # 6 -- optional alone, shape exists in the graph (lookup runs, no row)
    _call(EX.GuardShape, lambda: {EX.hasWindow: {"optional": True}}),
    # 7 -- optional False alone: the guard is false, minCount 1 is added
    _call(EX.GuardShape, lambda: {EX.hasWindow: {"optional": False}}),
    # 8 -- optional True with a second key: guard false on the key count
    _call(EX.GuardShape, lambda: {
        EX.hasWindow: {"optional": True, SKOS.definition: Literal("d")}}),
    # 9 -- no optional key at all
    _call(EX.GuardShape, lambda: {EX.hasWindow: {}}),
    # 10 -- or: two levels, an empty one, and beside a plain property
    _call(EX.OrShape, lambda: {
        "or": [
            {EX.a: {"datatype": XSD.string},
             "or": [{EX.b: {"values": ["x"]}}, {EX.c: {}}]},
            {"or": []},
            {EX.d: {"optional": False}},
        ],
        EX.plain: {"datatype": XSD.integer},
    }),
    # 11 -- import_from: every term kind is copied, ex:other is not
    _call(EX.ImportShape, lambda: {
        EX.hasImported: {"import_from": _IMPORT}}),
    # 12 -- import_from: a property with no triple in the file (zero rows)
    _call(EX.ImportShape, lambda: {
        EX.hasMissing: {"import_from": _IMPORT, "optional": True}}),
    # 13 -- import_from with optional False and a datatype
    _call(EX.ImportShape, lambda: {
        EX.hasImported: {"import_from": _IMPORT, "optional": False,
                         "datatype": XSD.string}}),
    # 14 -- import_from: a file that does not exist (raise)
    _call(EX.ImportShape, lambda: {
        EX.hasImported: {"import_from": str(_HERE / "no-such-file.ttl")}}),
    # 15 -- error: a property definition that is None
    _call(EX.ErrShape, lambda: {EX.first: {"datatype": XSD.string},
                                EX.hasNone: None}),
    # 16 -- error: `or` that is not iterable
    _call(EX.ErrShape, lambda: {"or": None}),
    # 17 -- error: a leftover `values` key (datatype wins, values is left
    #       for add_relationships, whose graph.add rejects a str predicate)
    _call(EX.ErrShape, lambda: {
        EX.both: {"datatype": XSD.string, "values": ["a"]}}),
    # 18 -- error: a leftover str key
    _call(EX.ErrShape, lambda: {EX.str: {"note": "x"}}),
    # 19 -- optional alone on the reflexive shapes of fixture.ttl: matched,
    #       min-constrained, max-constrained, and a path with no shape.  The
    #       lookup yields no row (SELECT ?x), so a new shape is written each
    #       time; a translation whose query could find the reflexive shape
    #       would write a different graph here.
    _call(EX.ReflexiveShape, lambda: {
        EX.hasReflexive: {"optional": True},
        EX.hasConstrained: {"optional": True},
        EX.hasMaxed: {"optional": True},
        EX.hasNowhere: {"optional": True},
    }),
]


VERDICT = run_pair(
    __file__,
    entry="define_shape_property_property",
    calls=CALLS,
    # No store promises an order among the SPARQL rows the region's read
    # branches match; each case below has at most one row to pick (the
    # fixture is built so), so ordered=True is safe and this is not a
    # `fixture=` run in the harness's single-argument sense.
    ordered=True,
)
