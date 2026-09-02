"""Validation driver for acdh-oeaw__acdh-django-vocabs__vocabs_skos_import.py__SkosImporter_parse_triples.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`parse_triples(self, g)` (see original.py for why `self` is an explicit
parameter and why the wrapper returns `concept_scheme`) only needs `self` to
have a `.language` attribute -- a plain `SimpleNamespace` stands in for the
real `SkosImporter` instance.

Only the "concept scheme found" branch is exercised: the region's `else:
raise Exception(...)` branch is real behaviour (both sides raise the same
way, unchanged), but `run_pair` aborts the whole comparison the moment
either side raises during a call, so there is no way to turn "both sides
raise identically" into a pass/fail here -- see rdfeval/harness.py. Every
fixture concept scheme therefore is typed skos:ConceptScheme; the read
patterns' zero-solution case is exercised at the FIELD level instead
(subject/publisher: no matching triples at all -- see fixture.ttl).
"""
from pathlib import Path
from types import SimpleNamespace

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
_SELF = SimpleNamespace(language="und")  # distinct from every @lang tag used
                                          # in fixture.ttl (en/fr/de), so the
                                          # language-fallback branch and the
                                          # tag-echo branch are visibly
                                          # different, not coincidentally equal


def _case():
    return ((_SELF, fixture_graph(FIXTURE)), {})


VERDICT = run_pair(
    __file__,
    entry='parse_triples',
    fixture="fixture.ttl",
    calls=[_case],
)
