"""Validation driver for aigora-de__rdf-construct__…__OntologyDeprecator_deprecate.

This region READS a graph and MUTATES it in place, so the oracle is not the
isomorphism of a freshly built graph but the equality of what both versions
produce from the same input graph (design record corpus/405): `fixture.ttl` is
parsed into a fresh graph for each side, for each call.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region's own return value is a `DeprecationResult`, and rdflib compares a
`Graph` field by store identifier, which two runs can never share.  `demo`
hands back the mutated graph itself (compared by isomorphism through the
harness's `normalise`) together with every counter the region computed.

The four calls walk the four paths through the region, and the *third* is the
one the `remove` stratum exists for: ex:OldClass carries two stale
dcterms:isReplacedBy values, and one `graph.remove((s, p, None))` — one
`-{ … ?old }` — has to take both.

`ordered=True`: what `demo` returns is a fixed-shape record, not a bag of
solutions; the two lists inside it that do come from the store (the labels and
the comments the region collected) are sorted by `demo` before comparison.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/onto#"


def case(*args, **kwargs):
    """A fresh input graph per side: the region modifies it in place."""
    return lambda: ((fixture_graph(FIXTURE),) + args, kwargs)


VERDICT = run_pair(
    __file__,
    entry="demo",
    fixture="fixture.ttl",
    ordered=True,
    calls=[
        # 1. plain entity, nothing to remove: only owl:deprecated is added
        case(EX + "PlainClass"),
        # 2. same entity, with a message but no pre-existing DEPRECATED
        #    comment: the bound removal does not fire
        case(EX + "PlainClass", message="Use ex:NewClass.", version="2.0"),
        # 3. THE remove case: two stale dcterms:isReplacedBy taken by one
        #    wildcard removal, and the one DEPRECATED comment taken by a
        #    fully bound one.  Already deprecated, so no owl:deprecated add.
        case(EX + "OldClass", replaced_by=EX + "NewClass",
             message="Use ex:NewClass instead.", version="2.0"),
        # 4. zero solutions: ex:Missing is never a subject -- early return,
        #    and the two references to it are counted
        case(EX + "Missing", replaced_by=EX + "NewClass", message="gone"),
    ],
)
