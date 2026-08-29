"""Validation driver for
city-knowledge-graphs__python-2023__lab6_OWLReasoning-solution.py__checkEntailment.

IDENTITY translation (see meta.json): `triple` is a whole triple PATTERN
held as an opaque string -- ":Carl :hasChild :Ann .", ":Ann rdf:type :Child .",
":Juliet :hasChild :Ann ." -- concatenated with `+` into the ASK query's body
(ASK { <triple> }). This is a motif of variable FORM (subject, predicate and
object all vary from one call to the next), spliced whole into the query
text, not a term: `s{ }`'s interpolation only stands where a TERM may stand
(querying.md), so there is no island for "an entire triple pattern held in a
variable" -- the same limit noted for `-{ }`/`m{ }` in INSTRUCTIONS_403 SS2,
here on the read side. Same region shape (and same limit) as lab4's
checkEntailment; see that pair's driver for the fuller argument.

checkEntailment(g, triple) only prints; the three real (g, triple)
invocations from upstream's own checkEntailments(g) (at the pinned commit)
are what proves the (unmodified) region still computes right -- one ASK
comes back True on fixture.ttl, two come back False.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent

TRIPLES = [
    ":Carl :hasChild :Ann .",
    ":Ann rdf:type :Child .",
    ":Juliet :hasChild :Ann .",
]


def _call(triple):
    # A fresh graph per call, and per side (run_pair invokes this twice per
    # entry in `calls`), so a mutation on one side cannot leak into the
    # other's input -- checkEntailment never mutates g, but this stays the
    # uniform, safe pattern for a fixture-backed multi-argument entry.
    return lambda: ((fixture_graph(HERE / "fixture.ttl"), triple), {})


VERDICT = run_pair(
    __file__,
    entry='checkEntailment',
    calls=[_call(t) for t in TRIPLES],
    # ASK has no row order to speak of, but hand-built calls= (needed
    # because checkEntailment takes two arguments, not the one fixture=
    # alone would pass) does not default ordered=False on its own the way
    # fixture= does -- say so explicitly.
    ordered=False,
)
