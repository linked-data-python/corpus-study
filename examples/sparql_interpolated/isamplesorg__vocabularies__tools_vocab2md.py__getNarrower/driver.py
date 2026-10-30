"""Validation driver for isamplesorg__vocabularies__tools_vocab2md.py__getNarrower.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

The first three calls pass `v` and `r` as `str`, and on an in-memory graph a
`str` in `initBindings` matches no IRI: they return [] on both sides and
prove nothing about the query.  The repository never passes a `str`: in
tools/vocab2md.py `r` is a row of a query result (`getVocabRoot`, :178-189,
then `getNarrower`'s own results when `termTree`/`termJsonTree`/
`describeNarrowerTerms` recurse, :242, :256, :309), so an `rdflib.URIRef`,
and the graph is an in-memory `rdflib.Graph` parsed from the vocabulary file.
The URIRef calls below (repair of 2026-10-30) are the ones that exercise the
query; each one makes a different term decide:

- r=Animal, v=None: five solutions (Dog, Cat, Wolf, Horse, Lynx once); the
  skos:related neighbour Cactus and the broader-than-Plant Fish stay out;
- r=Animal, v=VocabA: Dog, Cat, Lynx -- Wolf (other scheme) and Horse (tied
  to VocabA by skos:topConceptOf, not skos:inScheme) stay out;
- r=Animal, v=VocabB: Wolf and Lynx -- the scheme term, not just its
  presence, decides; Lynx (in both schemes) comes back once;
- r=Plant, v=VocabA: Fish -- the broader term decides inside the v branch;
- r=Rock, v=None and r=Rock, v=VocabA: zero solutions in each branch;
- r=Animal, v=VocabC: zero solutions, a scheme nobody is in.

`v` is None at every real call site (`narrower_v = None`, :343); the v
branch is exercised all the same because the region has it.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph

EX = Namespace("http://example.org/")

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(v, r):
    return lambda: ((fixture_graph(FIXTURE), v, r), {})


VERDICT = run_pair(
    __file__,
    entry='getNarrower',
    calls=[
        call(None, "http://example.org/Animal"),                   # several solutions: Dog, Cat
        call("http://example.org/VocabA", "http://example.org/Animal"),  # scheme filter excludes Wolf
        call(None, "http://example.org/Rock"),                     # zero solutions
        # the type the repository really passes (see the docstring)
        call(None, EX.Animal),
        call(EX.VocabA, EX.Animal),
        call(EX.VocabB, EX.Animal),
        call(EX.VocabA, EX.Plant),
        call(None, EX.Rock),
        call(EX.VocabA, EX.Rock),
        call(EX.VocabC, EX.Animal),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
