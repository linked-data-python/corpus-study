"""Validation driver for ktbs__ktbs__lib_ktbs_api_trace.py__StoredTraceMixin_create_obsel.

Establishes semantic equivalence of original.py and translated.ldpy via the
demo(**kwargs) harness both files carry (see meta.json): create_obsel builds
its graph and hands it to self.post_graph(...), a side effect rather than a
return value, so demo() supplies a context_shim._TraceStub as `self` and
hands back the graph it captured.

Three calls, chosen to walk every branch that touches the graph (the ones
that raise -- "type is mandatory", unparsable begin/end -- are not
RDF-producing branches and are left untested here):

CALL_1 -- begin/end as plain ints (hasBegin/hasEnd, not the DT variants),
an explicit URIRef subject, and all four "in a loop" collections non-empty
and multi-item: attributes (one Node-valued, one plain-valued -- exercises
both sides of `val if isinstance(val, Node) else Literal(val)`), relations,
inverse_relations, source_obsels. This is the main add-in-loop exhibit.

CALL_2 -- begin as an ISO date string (the parse_date branch), end as a
naive datetime (the "tzinfo is None -> replace(tzinfo=UTC)" branch),
subject=None (self.get_default_subject()), id=None (BNode obs -- graph
isomorphism, not identity, so a fresh blank node each run is fine), and all
four loop collections absent (None) -- the loops must contribute nothing.

CALL_3 -- subject given as a plain string, not a URIRef (the
Literal(subject) branch), begin as a tz-aware datetime (Integral branch not
taken, tzinfo already set so no replace()), end as an int, a label, and all
four loop collections present but EMPTY -- zero iterations, not "loop
absent": a bindings-generator with nothing to yield must still add nothing
extra, not raise.
"""
from rdfeval.harness import run_pair
from datetime import datetime, timezone
from rdflib import URIRef

CALL_1 = {}, {
    "id": "http://example.org/obs/o1",
    "type": "http://example.org/model#Event",
    "begin": 1000,
    "end": 2000,
    "subject": "http://example.org/subjects/s1",
    "attributes": {
        "http://example.org/attr#weight": 42,
        "http://example.org/attr#ref": URIRef("http://example.org/other"),
    },
    "relations": [
        ("http://example.org/rel#next", "http://example.org/obs/o2"),
    ],
    "inverse_relations": [
        ("http://example.org/obs/o0", "http://example.org/rel#prev"),
    ],
    "source_obsels": [
        "http://example.org/obs/src1",
        "http://example.org/obs/src2",
    ],
    "label": "First obsel",
}

CALL_2 = {}, {
    "id": None,
    "type": "http://example.org/model#Sample",
    "begin": "2020-01-01T10:00:00Z",
    "end": datetime(2020, 1, 1, 10, 5, 0),
    "subject": None,
    "attributes": None,
    "relations": None,
    "inverse_relations": None,
    "source_obsels": None,
    "label": None,
}

CALL_3 = {}, {
    "id": "http://example.org/obs/o3",
    "type": "http://example.org/model#Event",
    "begin": datetime(2020, 6, 1, 8, 0, 0, tzinfo=timezone.utc),
    "end": 3000,
    "subject": "plain-string-subject",
    "attributes": {},
    "relations": [],
    "inverse_relations": [],
    "source_obsels": [],
    "label": "Third obsel",
}

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[CALL_1, CALL_2, CALL_3],
)
