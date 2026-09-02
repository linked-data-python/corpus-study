"""Validation driver for
matthiasprobst__ontology-utils__ontolutils_classes_query_util.py__dquery.

IDENTITY translation (see meta.json): `dquery` assembles its whole SPARQL
query text at RUN TIME, not just a term in an otherwise-written query. Two
things put it out of `s{ }`'s reach, both about the query's STRUCTURE, not
merely its terms:

  * the PREFIX prologue is built by looping over the `context` dict the
    caller passes in -- a variable number of `PREFIX k: <p>` lines, decided
    only when `dquery` runs:
      prefixes = "".join([f"PREFIX {k}: <{p}>\\n"
                           for k, p in context.items() if not k.startswith('@')])
    `s{ }` is parsed when the FILE is transpiled (querying.md); its prologue
    comes from `@prefix` declarations resolved at that point, never from a
    dict handed to a function at call time -- there is no way to add "one
    `@prefix` per key of a dict I only have at runtime" to a written query.
  * `subject` is spliced as raw SPARQL syntax (`?id a {subject}.`), not
    coerced as a term: the string `"prov:Agent"` (the docstring's own
    example) only means anything because it lands, unparsed, inside a query
    text that also carries a matching PREFIX line built the same way.
    `s{ }`'s `{expr}` interpolation always runs the term coercion policy --
    a bare `str` becomes a `Literal` -- which cannot reproduce "this string
    is already a fragment of SPARQL syntax, splice it verbatim".

Both failures are about assembling the query's SHAPE dynamically (how many
prologue lines; what a "term" slot even means at that site), the thing
INSTRUCTIONS.md SS2 says `s{ }`'s interpolation can never do (it lowers to an
initBindings, never string-pasting). Nothing here maps to any ldpy island,
so translated.ldpy is an unmodified copy of original.py (down to the same
context_shim import for the sibling helpers dquery calls).

This region READS a graph, so the oracle is value equality (corpus/405), not
isomorphism. `dquery` never receives a graph directly, though: it parses its
own from `data=` (JSON-LD only -- `format='json-ld'` is hard-coded). So the
generic `fixture=` shortcut -- which hands the entry a Turtle-parsed Graph as
its one positional argument -- does not fit `dquery`'s signature at all.
fixture.ttl is instead parsed once, with rdflib, and re-serialised to the
JSON-LD string every call passes as `data=` -- exactly what a caller of
dquery holding a Turtle file would have to do, since dquery itself offers no
other entry point.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent

# Parsed once, from the same Turtle fixture, and reused verbatim by every
# call on both sides: `data=` is a plain string dquery only ever reads, so
# there is no mutation risk that would call for a fresh copy per call (unlike
# a live Graph passed to a region that might write to it).
_DATA = fixture_graph(HERE / "fixture.ttl").serialize(format="json-ld")
_CONTEXT = {"ex": "http://example.org/"}

CALLS = [
    # several solutions: two ex:Agent individuals (see fixture.ttl) --
    # `?id ?p ?o` also yields the `rdf:type` row for each, which
    # expand_sparql_res folds into '@type' rather than a data key.
    ((), dict(subject="ex:Agent", data=_DATA, context=_CONTEXT)),
    # the zero-solution case: no ex:Ghost instance in the fixture.
    ((), dict(subject="ex:Ghost", data=_DATA, context=_CONTEXT)),
]

VERDICT = run_pair(
    __file__,
    entry="dquery",
    calls=CALLS,
    # dquery returns `[v for v in kwargs.values()]`, built from
    # `res.bindings` in whatever order the store yields solutions: no store
    # promises one, and this region has no ORDER BY / sort to fix it.
    ordered=False,
)
