"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_validate_bfo_ontology.py__check_restriction_references.

This region READS a graph (several `g.value`/`g.subjects` calls over
owl:Restriction bnodes), so the oracle is not isomorphism of a graph the
region builds but the equality of what the two versions produce from the same
input (design record corpus/405): `fixture.ttl` is parsed fresh for each side
and fed as the sole argument `g`.

The fixture (see its own header) covers: several owl:Restriction bnodes
reached from different owner classes, exercising both filler predicates
(allValuesFrom / someValuesFrom) and the vocabulary-prefix / declared-term /
graph-membership branches of `_is_known`; the zero-solution case for
`m{ ?owner rdfs:subClassOf {bnode} }.first()` (an orphan restriction with no
owner, which must be skipped via `continue`); and neighbourhood triples
(an ordinary subclass edge, an unrelated onProperty-shaped triple on an
unreached bnode) that must not be picked up.
"""
from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"


def one_call():
    return ((fixture_graph(FIXTURE),), {})


VERDICT = run_pair(
    __file__,
    entry='check_restriction_references',
    fixture=FIXTURE,
    calls=[one_call],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
