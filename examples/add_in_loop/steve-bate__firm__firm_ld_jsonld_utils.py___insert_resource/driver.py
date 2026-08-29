"""Validation driver for steve-bate__firm__firm_ld_jsonld_utils.py___insert_resource.

Establishes semantic equivalence of original.py and translated.ldpy.

_insert_resource takes an already-expanded JSON-LD-shaped dict and returns
the subject it inserted; the graph it built is reached through the mutable
`g` argument, so run_pair's per-call argument comparison (not just the
return value) is what proves the two graphs match -- each call passes a
fresh Graph() (calls are callables, invoked once per side, per
rdfeval.harness.run_pair's docstring on mutable arguments).

RESOURCE_1 exercises: an explicit "@id" subject, a multi-valued "@type"
(the add-in-loop the stratum targets), a single "@value" object (Literal),
a single "@id" object (URIRef reference), and a nested object with two keys
that recurses into _insert_resource (a fresh BNode subject).

RESOURCE_2 exercises: no "@id" (BNode subject), a single-valued "@type", the
same predicate repeated over two distinct "@id" objects (two triples, one
subject/predicate, from one loop iteration group), and an empty "@list"
(the "continue" branch -- zero triples, no error). The non-empty "@list"
branch (`raise Exception("@list not supported")`) is deliberately not
exercised: it is a real behaviour of the region, but comparing two runs that
are BOTH expected to raise is not what run_pair's per-call try/except is
for -- it would abort the whole driver rather than compare anything.
"""
from rdfeval.harness import run_pair

RESOURCE_1 = {
    "@id": "http://example.org/alice",
    "@type": [
        "http://example.org/Person",
        "http://example.org/Agent",
    ],
    "http://example.org/name": [{"@value": "Alice"}],
    "http://example.org/knows": [{"@id": "http://example.org/bob"}],
    "http://example.org/address": [
        {
            "http://example.org/city": [{"@value": "Paris"}],
            "http://example.org/zip": [{"@value": "75000"}],
        }
    ],
}

RESOURCE_2 = {
    "@type": ["http://example.org/Thing"],
    "http://example.org/related": [
        {"@id": "http://example.org/x1"},
        {"@id": "http://example.org/x2"},
    ],
    "http://example.org/empty": [{"@list": []}],
}


def _case(resource):
    def make():
        import rdflib
        return (rdflib.Graph(), resource), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='_insert_resource',
    calls=[_case(RESOURCE_1), _case(RESOURCE_2)],
)
