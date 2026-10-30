"""Validation driver for aigora-de__rdf-construct__…__OntologyMerger_merge_graphs.

The region READS two graphs and BUILDS a third, so the oracle combines both:
`fixture.ttl` (the existing ontology), `fixture_new.ttl` (the freshly
generated graph) and `fixture_empty.ttl` (the zero-solution case) are parsed
into fresh graphs for each side and for each call, and what is compared is the
merged graph -- by RDF isomorphism, through the harness's `normalise` -- plus
the four statistics the region computes.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region's own return value is a `MergeResult`, and rdflib compares a
`Graph` field by store identifier, which two runs can never share.

The `remove` site is `result.graph.remove((s, p, ev))`, reached only when the
new graph offers several values for one authoritative predicate AND
`preserve_existing` is False -- hence the first two calls, which differ by
that flag alone: the same conflicts are reported both times, and only the
first actually removes (two removals, three rdfs:subClassOf collapsing to one).

Neighbours (fixtures): every triple the region tests, reads or removes has a
neighbour that shares two of its terms.  ex:Sensor rdfs:seeAlso ex:Device,
ex:Component, ex:Physical (existing) share subject and object with the three
new rdfs:subClassOf values; ex:Actuator rdfs:seeAlso ex:Device (existing) and
ex:Actuator rdfs:subClassOf ex:Device (new) likewise; ex:Sensor rdfs:domain
ex:Env in the new graph is the same predicate under another subject than the
existing ex:Actuator rdfs:domain ex:System; ex:Sensor rdfs:range "", 0, "0"
(new) gives falsy existing values (ev) to the conflict loop.  Mutants run in a
copy (translated.ldpy, one change each), all FAIL, also under two values of
PYTHONHASHSEED: the removal replaced by `pass`; its subject or its predicate
widened to a variable; the predicate, subject or object of the `not m{ }`
existence test widened, or the test forced True; the subject or predicate of
`m{ ... ?nv }(new_graph)` widened, or that read pointed at `existing`; the
subject or predicate of `list(m{ ... ?ev })` widened; `if new_values` ->
`any(new_values)`; `ev != o` -> `ev != o and ev`; the `preserve_existing` test
inverted.  Two mutants stay green and are equivalent: the removal's object
widened (at removal time result.graph holds only values of (s, p) that the
loop removes anyway, as the translation notes say) and `ev != o` forced True
(the `not in result.graph` test above has already excluded ev == o).

`ordered=True`: `demo` returns a fixed-shape record, and the one list in it
(the conflict messages) is sorted before comparison.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent
EXISTING, NEW, EMPTY = "fixture.ttl", "fixture_new.ttl", "fixture_empty.ttl"


def case(new, existing, **kwargs):
    """A fresh pair of input graphs per side."""
    return lambda: ((fixture_graph(HERE / new), fixture_graph(HERE / existing)),
                    dict(kwargs))


VERDICT = run_pair(
    __file__,
    entry="demo",
    fixture="fixture.ttl",
    ordered=True,
    calls=[
        # 1. THE remove case: preserve_existing=False, so each conflict on an
        #    authoritative predicate removes the value already merged
        case(NEW, EXISTING, preserve_existing=False),
        # 2. same input, preserve_existing=True: the conflicts are reported
        #    and nothing is removed -- the control for call 1
        case(NEW, EXISTING, preserve_existing=True),
        # 3. zero solutions: an empty new graph, everything is preserved
        case(EMPTY, EXISTING, preserve_existing=False),
        # 4. the two roles swapped, to walk the branches the other way round
        case(EXISTING, NEW, preserve_existing=False),
    ],
)
