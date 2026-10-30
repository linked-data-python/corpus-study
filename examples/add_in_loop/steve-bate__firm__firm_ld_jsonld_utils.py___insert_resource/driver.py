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
(the "continue" branch -- zero triples, no error). RESOURCE_3 (non-empty "@list") reaches the branch
`raise Exception("@list not supported")`: run_pair compares what a call
raised (type and message), the printed JSON of the except handler, and what
the call had already written to `g` before raising.

RESOURCE_4 is a nested node with a SINGLE property and neither "@id", "@value"
nor "@list" (e.g. an address with one field, or a node that only has "@type"
-- here {"http://example.org/q": [{"@value": "v"}]}). It does reach the
function in the repository: firm/ld/jsonld_utils.py:jsonld_to_graph calls
_insert_resource on the output of jsonld.expand, where every nested node with
one property has len(obj) == 1. The original hands the dict to `g.add`, which
rejects it (AssertionError "must be an rdflib term"); the translation must
raise the same, not coerce the dict to a Literal. RESOURCE_5 mixes a nested
single-property node among terms that are written before it, and
RESOURCE_6 has a nested node with "@id" plus another property (the
recursive branch, an "@id" object of len 2) next to an "@id"+"@value" object
of len 2 (the "@value" wins).
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


RESOURCE_3 = {
    "@id": "http://example.org/c",
    "http://example.org/p": [
        {"@id": "http://example.org/before"},
        {"@list": [{"@id": "http://example.org/item"}]},
    ],
}

RESOURCE_4 = {
    "@id": "http://example.org/a",
    "http://example.org/p": [{"http://example.org/q": [{"@value": "v"}]}],
}

RESOURCE_5 = {
    "@id": "http://example.org/m",
    "@type": ["http://example.org/Thing"],
    "http://example.org/name": [{"@value": "M"}],
    "http://example.org/p": [{"@id": "http://example.org/ok"},
                             {"@type": ["http://example.org/Only"]}],
}

RESOURCE_6 = {
    "@id": "http://example.org/n",
    "http://example.org/p": [
        {"@id": "http://example.org/n2", "http://example.org/r": [{"@value": "w"}]},
        {"@id": "http://example.org/ignored", "@value": "both"},
    ],
}


def _case(resource):
    def make():
        import rdflib
        return (rdflib.Graph(), resource), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='_insert_resource',
    calls=[_case(RESOURCE_1), _case(RESOURCE_2), _case(RESOURCE_3),
           _case(RESOURCE_4), _case(RESOURCE_5), _case(RESOURCE_6)],
)
